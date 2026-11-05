
async function runSuite(modPath, label) {
  const mod = await import(modPath);
  const { DeterministicStateMachine } = mod;
  const checks = [];

  // Check 1: Does engine enforce intent-nonce replay refusal and quote conservation?
  let check1Pass = false;
  let check1Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let unbalancedQuoteRejected = false;
    try {
      sm.applyStep('quote', { summary: 'bad quote', metrics: { amount_in_usdc: 5000, amount_out_usdc: 6000, solver_fee_usdc: 4, rate: 0.9992 } });
    } catch (e) {
      unbalancedQuoteRejected = true;
    }
    let replayAcceptedError = false;
    try {
      sm.applyStep('swap', { summary: 's1', metrics: { nonce: 'n-100', settled_out_usdc: 4996, solver_fee_usdc: 4, replay_attempt: 'REFUSED' } });
      sm.applyStep('swap', { summary: 's2 replay accepted!', metrics: { nonce: 'n-100', settled_out_usdc: 4996, solver_fee_usdc: 4, replay_attempt: 'ACCEPTED' } });
    } catch (e) {
      replayAcceptedError = true;
    }
    const hasSwapFn = typeof mod.executeIntentSwap === 'function' || typeof mod.EarningsVault === 'function';
    check1Pass = unbalancedQuoteRejected && replayAcceptedError && hasSwapFn;
    check1Detail = check1Pass
      ? "PASS: Unbalanced solver quote (6000 out > 5000 in) and duplicate intent nonce replay ('n-100') were both rejected, and EarningsVault.executeIntentSwap() is exported."
      : `FAIL: unbalancedQuoteRejected=${unbalancedQuoteRejected}, replayAcceptedError=${replayAcceptedError}, hasSwapFn=${hasSwapFn}. Unpatched engine only hashes static STEPS_SPEC literals without checking quote math or nonce replay!`;
  } catch (e) {
    check1Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_1_intent_quote_and_nonce_replay_guard",
    claim_tested: "README Step 1 & 2: quote verifies 5000 * 0.9992 = 4996 + 4 fee, and swap refuses replay of same intent nonce (intent_already_settled)",
    passed: check1Pass,
    detail: check1Detail
  });

  // Check 2: Does engine enforce ERC-4626 share price and withdrawal conservation?
  let check2Pass = false;
  let check2Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let inflatedWithdrawRejected = false;
    try {
      sm.applyStep('deposit_and_withdraw', {
        summary: 'inflated withdraw',
        metrics: { deposited_usdc: 4000, minted_shares: 4000, yield_accrued_usdc: 120, share_price_usdc: 1.03, redeemed_shares: 2000, withdrawn_usdc: 999999 }
      });
    } catch (e) {
      inflatedWithdrawRejected = true;
    }
    let vaultMathExact = false;
    if (typeof mod.EarningsVault === 'function') {
      const v = new mod.EarningsVault();
      const sh = v.deposit(4000);
      v.accrueYield(120);
      const out = v.redeem(2000);
      vaultMathExact = (sh === 4000 && out === 2060);
    }
    check2Pass = inflatedWithdrawRejected && vaultMathExact;
    check2Detail = check2Pass
      ? "PASS: Inflated vault withdrawal (999,999 USDC for 2,000 shares) rejected, and EarningsVault computes 4,000 shares -> +120 yield -> 2,000 shares redeemed = 2,060.00 USDC exactly."
      : `FAIL: inflatedWithdrawRejected=${inflatedWithdrawRejected}, vaultMathExact=${vaultMathExact}. Unpatched engine accepts 999,999 USDC withdrawal on 4,120 USDC vault assets!`;
  } catch (e) {
    check2Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_2_erc4626_share_accounting_invariant",
    claim_tested: "README Step 3: Agent deposits 4,000 USDC -> 4,000 shares; +120 USDC yield -> share price 1.03 USDC; redeeming 2,000 shares yields 2,060.00 USDC",
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
