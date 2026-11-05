
async function runSuite(modPath, label) {
  const mod = await import(modPath);
  const { DeterministicStateMachine } = mod;
  const checks = [];

  // Check 1: Does engine block low-reputation spenders (reputation < 65) from approving shared budget spends?
  let check1Pass = false;
  let check1Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let lowRepBypassBlocked = false;
    try {
      sm.applyStep('shared_budget_spend', {
        summary: 'low rep bypass',
        metrics: { actor: 'attacker.near', budget_id: 'q4-growth', spend_usdc: 1200, reputation: 41, min_reputation: 65, status: 'APPROVED', remaining_budget_usdc: 3800, vault_balance_usdc: 48800 }
      });
    } catch (e) {
      lowRepBypassBlocked = true;
    }
    let evalFnWorks = false;
    if (typeof mod.evaluateBudgetSpend === 'function') {
      const ok = mod.evaluateBudgetSpend({ budgetRemainingUsdc: 5000, vaultBalanceUsdc: 50000, spendUsdc: 1200, reputation: 82, minReputation: 65 });
      const ref = mod.evaluateBudgetSpend({ budgetRemainingUsdc: 3800, vaultBalanceUsdc: 48800, spendUsdc: 500, reputation: 41, minReputation: 65 });
      evalFnWorks = (ok.status === 'APPROVED' && ok.remaining_budget_usdc === 3800 && ref.status === 'REFUSED' && ref.remaining_budget_usdc === 3800);
    }
    check1Pass = lowRepBypassBlocked && evalFnWorks;
    check1Detail = check1Pass
      ? "PASS: Low-reputation spend (rep 41 < gate 65 with status=APPROVED) rejected, and evaluateBudgetSpend() enforces the gate and preserves the 3,800 USDC budget."
      : `FAIL: lowRepBypassBlocked=${lowRepBypassBlocked}, evalFnWorks=${evalFnWorks}. Unpatched engine approves shared_budget_spend with reputation 41 < 65!`;
  } catch (e) {
    check1Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_1_reputation_gate_and_budget_preservation",
    claim_tested: "README Step 1 & 3: reputation >= 65 required for shared_budget_spend; newcomer-eve (rep 41 < 65) is REFUSED and budget stays 3,800 USDC",
    passed: check1Pass,
    detail: check1Detail
  });

  // Check 2: Does reward_payout enforce 3/3 steward quorum and block duplicate milestone claims?
  let check2Pass = false;
  let check2Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let unapprovedQuorumBlocked = false;
    try {
      sm.applyStep('reward_payout', {
        summary: '1/3 stewards only',
        metrics: { actor: 'builder-bob.near', milestone: 'M-104', steward_approvals: 1, reward_usdc: 450, reputation_delta: 18, new_reputation: 78, status: 'RELEASED' }
      });
    } catch (e) {
      unapprovedQuorumBlocked = true;
    }
    sm.applyStep('reward_payout', {
      summary: 'valid 3/3',
      metrics: { actor: 'builder-bob.near', milestone: 'M-104', steward_approvals: 3, reward_usdc: 450, reputation_delta: 18, new_reputation: 78, status: 'RELEASED' }
    });
    let duplicateMilestoneBlocked = false;
    try {
      sm.applyStep('reward_payout', {
        summary: 'replay M-104',
        metrics: { actor: 'builder-bob.near', milestone: 'M-104', steward_approvals: 3, reward_usdc: 450, reputation_delta: 18, new_reputation: 96, status: 'RELEASED' }
      });
    } catch (e) {
      duplicateMilestoneBlocked = true;
    }
    check2Pass = unapprovedQuorumBlocked && duplicateMilestoneBlocked;
    check2Detail = check2Pass
      ? "PASS: Sub-quorum reward release (1/3 stewards) and duplicate milestone replay ('M-104') were both blocked."
      : `FAIL: unapprovedQuorumBlocked=${unapprovedQuorumBlocked}, duplicateMilestoneBlocked=${duplicateMilestoneBlocked}. Unpatched engine releases rewards with 1/3 stewards and allows claiming M-104 repeatedly!`;
  } catch (e) {
    check2Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_2_steward_quorum_and_milestone_replay_guard",
    claim_tested: "README Step 2: milestone M-104 verified by 3/3 stewards releases 450 USDC + 18 reputation points once",
    passed: check2Pass,
    detail: check2Detail
  });

  return { label, checks };
}

import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const origUrl = pathToFileURL(path.join(__dirname, 'original', 'src', 'engine.mjs')).href;
const impUrl = pathToFileURL(path.join(__dirname, '..', 'improved', 'src', 'engine.mjs')).href;

const origRes = await runSuite(origUrl, 'original_engine_mjs');
const impRes = await runSuite(impUrl, 'improved_engine_mjs');
console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
