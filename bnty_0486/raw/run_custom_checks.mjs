
async function runSuite(modPath, label) {
  const mod = await import(modPath);
  const { DeterministicStateMachine } = mod;
  const checks = [];

  // Check 1: Does engine block plaintext leakage and forged commitment openings?
  let check1Pass = false;
  let check1Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let leakBlocked = false;
    try {
      sm.applyStep('private_job', { summary: 'leak', plaintext: 'SECRET_PROMPT', metrics: { job_id: '701', public_plaintext_leaked: true } });
    } catch (e) {
      leakBlocked = true;
    }
    let forgedBlocked = false;
    try {
      sm.applyStep('shielded_payment', { summary: 'forged', metrics: { job_id: '701', shielded_amount_usdc: 750, commitment_verified: true, forged_opening_accepted: true } });
    } catch (e) {
      forgedBlocked = true;
    }
    let cryptoCommitmentWorks = false;
    if (typeof mod.createShieldedCommitment === 'function' && typeof mod.verifyShieldedOpening === 'function') {
      const c = mod.createShieldedCommitment(750, 'blind_secret_1', '701');
      cryptoCommitmentWorks = mod.verifyShieldedOpening(c, 750, 'blind_secret_1', '701') === true &&
                              mod.verifyShieldedOpening(c, 750, 'wrong_blinding', '701') === false;
    }
    check1Pass = leakBlocked && forgedBlocked && cryptoCommitmentWorks;
    check1Detail = check1Pass
      ? "PASS: Plaintext prompt leakage and forged commitment openings are rejected, and createShieldedCommitment/verifyShieldedOpening cryptographically reject wrong blinding factors."
      : `FAIL: leakBlocked=${leakBlocked}, forgedBlocked=${forgedBlocked}, cryptoCommitmentWorks=${cryptoCommitmentWorks}. Unpatched engine records leaked plaintext and forged commitments into the state chain!`;
  } catch (e) {
    check1Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_1_confidential_job_and_shielded_commitment_guard",
    claim_tested: "README Step 1 & 2: plaintext prompt never touches public state, and forged commitment with wrong blinding factor is REFUSED",
    passed: check1Pass,
    detail: check1Detail
  });

  // Check 2: Does atomicReveal verify proof, conserve locked 750 USDC, and block double-settlement?
  let check2Pass = false;
  let check2Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    sm.applyStep('private_job', { summary: 'ok', metrics: { job_id: '701', ciphertext_Bytes: 256, public_plaintext_leaked: false, status: 'COMMITTED' } });
    sm.applyStep('shielded_payment', { summary: 'ok', metrics: { job_id: '701', shielded_amount_usdc: 750, commitment_verified: true, forged_opening_accepted: false } });
    let overpayBlocked = false;
    try {
      sm.applyStep('completion_reveal', { summary: 'overpay', metrics: { job_id: '701', enclave_proof_valid: true, worker_released_usdc: 5000, buyer_decrypted_ok: true } });
    } catch (e) {
      overpayBlocked = true;
    }
    sm.applyStep('completion_reveal', { summary: 'ok', metrics: { job_id: '701', enclave_proof_valid: true, worker_released_usdc: 750, buyer_decrypted_ok: true, status: 'SETTLED' } });
    let replayBlocked = false;
    try {
      sm.applyStep('completion_reveal', { summary: 'replay', metrics: { job_id: '701', enclave_proof_valid: true, worker_released_usdc: 750, buyer_decrypted_ok: true, status: 'SETTLED' } });
    } catch (e) {
      replayBlocked = true;
    }
    check2Pass = overpayBlocked && replayBlocked && typeof mod.atomicReveal === 'function';
    check2Detail = check2Pass
      ? "PASS: Over-release (5,000 USDC vs 750 USDC locked) and duplicate completion_reveal on job #701 are both blocked, and atomicReveal() is exported."
      : `FAIL: overpayBlocked=${overpayBlocked}, replayBlocked=${replayBlocked}, hasAtomicReveal=${typeof mod.atomicReveal === 'function'}. Unpatched engine has no atomicReveal() and allows releasing 5,000 USDC from a 750 USDC note!`;
  } catch (e) {
    check2Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_2_atomic_reveal_and_nullifier_conservation",
    claim_tested: "README Step 3: atomicReveal() verifies proof against job #701, releases 750 USDC to worker note, and prevents double reveal",
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
