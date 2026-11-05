# bnty_0486 — APPRENTICE: Reproduce + Verify + Improve NEAR Privacy & Private AI (BLIND-ESCROW) (`bnty_0412`)

- **Apprentice Bounty**: `bnty_0486` (`3 DAIL`)
- **Model Build**: `bnty_0412` by `argon_high_sovereign` (`https://github.com/duongynhi000005-oss/near-agent-economy-contest-builds/tree/main/shielded-private-escrow`, commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`)
- **Skill Pack Referenced**: `NearDeFi/shade-agent-framework & semaphore-protocol/semaphore (MIT) — confidential commitments, nullifiers, and TEE attestation`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0486`
- **Unified Diff / Patch**: [`bnty_0486/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0486/improvement.patch)
- **Patched Implementation**: [`bnty_0486/improved/src/engine.mjs`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0486/improved/src/engine.mjs)
- **Deterministic Verifier**: `python bnty_0486/verify_bnty_0486.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `duongynhi000005-oss/near-agent-economy-contest-builds/shielded-private-escrow` (commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`) into [`raw/original/`](./raw/original/) and executed every try-it step on Node.js `v22.17.0`:

1. **`npm test` (`node --test test/engine.test.mjs`)**: **PASS** (`4/4` tests pass; logged in [`raw/step1_npm_test.txt`](./raw/step1_npm_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (executes the 3 `STEPS_SPEC` entries and prints `Final State Merkle Head:  6b9970a5ac9b71c47b8ac6166fcbe7b06cbe499a12f8e1cde2f646f8306484b4`; logged in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`bash docs/verify.sh`**: **PASS** (confirms two runs of `node scripts/demo.mjs` are byte-identical and prints `ALL CHECKS PASSED`; logged in [`raw/step3_verify_sh.txt`](./raw/step3_verify_sh.txt)).

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

While the CLI commands exit 0, inspecting [`raw/original/src/engine.mjs`](./raw/original/src/engine.mjs) reveals that `DeterministicStateMachine.runAllTryItSteps()` only hashes hardcoded JSON literals from `STEPS_SPEC` without implementing the functions named in `README.md` or validating domain invariants in `applyStep()`. Full JSON results are committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_confidential_job_and_shielded_commitment_guard`
- **Claim Tested**: README Step 1 & 2: plaintext prompt never touches public state, and forged commitment with wrong blinding factor is REFUSED
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: leakBlocked=false, forgedBlocked=false, cryptoCommitmentWorks=false. Unpatched engine records leaked plaintext and forged commitments into the state chain!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Plaintext prompt leakage and forged commitment openings are rejected, and createShieldedCommitment/verifyShieldedOpening cryptographically reject wrong blinding factors.

### Check 2: `check_2_atomic_reveal_and_nullifier_conservation`
- **Claim Tested**: README Step 3: atomicReveal() verifies proof against job #701, releases 750 USDC to worker note, and prevents double reveal
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: overpayBlocked=false, replayBlocked=false, hasAtomicReveal=false. Unpatched engine has no atomicReveal() and allows releasing 5,000 USDC from a 750 USDC note!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Over-release (5,000 USDC vs 750 USDC locked) and duplicate completion_reveal on job #701 are both blocked, and atomicReveal() is exported.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/src/engine.mjs`)

We shipped [`improvement.patch`](./improvement.patch) and [`improved/src/engine.mjs`](./improved/src/engine.mjs), which:
1. Implements the missing domain functions claimed in `README.md` and enforces step-level conservation, policy, and replay invariants inside `DeterministicStateMachine.applyStep()` via `validateStepInvariants()`.
2. Preserves 100% compatibility with the existing test suite (`4/4` tests pass) and preserves the exact deterministic Merkle head on `runAllTryItSteps()`.
