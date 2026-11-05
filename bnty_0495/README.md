# bnty_0495 — APPRENTICE: Reproduce + Verify + Improve NEAR Social Money (TREZU-SOCIAL) (`bnty_0422`)

- **Apprentice Bounty**: `bnty_0495` (`3 DAIL`)
- **Model Build**: `bnty_0422` by `argon_high_sovereign` (`https://github.com/duongynhi000005-oss/near-agent-economy-contest-builds/tree/main/trezu-social-money`, commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`)
- **Skill Pack Referenced**: `erc-8004/erc-8004-contracts (CC0) — reputation-gated Sputnik DAO / Trezu shared budgets and milestone reward streams`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0495`
- **Unified Diff / Patch**: [`bnty_0495/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0495/improvement.patch)
- **Patched Implementation**: [`bnty_0495/improved/src/engine.mjs`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0495/improved/src/engine.mjs)
- **Deterministic Verifier**: `python bnty_0495/verify_bnty_0495.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `duongynhi000005-oss/near-agent-economy-contest-builds/trezu-social-money` (commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`) into [`raw/original/`](./raw/original/) and executed every try-it step on Node.js `v22.17.0`:

1. **`npm test` (`node --test test/engine.test.mjs`)**: **PASS** (`4/4` tests pass; logged in [`raw/step1_npm_test.txt`](./raw/step1_npm_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (executes the 3 `STEPS_SPEC` entries and prints `Final State Merkle Head:  665465ae2267e2ccb52b116e34f32d43990cdfbe21997bfb5ae62487f2e01826`; logged in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`bash docs/verify.sh`**: **PASS** (confirms two runs of `node scripts/demo.mjs` are byte-identical and prints `ALL CHECKS PASSED`; logged in [`raw/step3_verify_sh.txt`](./raw/step3_verify_sh.txt)).

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

While the CLI commands exit 0, inspecting [`raw/original/src/engine.mjs`](./raw/original/src/engine.mjs) reveals that `DeterministicStateMachine.runAllTryItSteps()` only hashes hardcoded JSON literals from `STEPS_SPEC` without implementing the functions named in `README.md` or validating domain invariants in `applyStep()`. Full JSON results are committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_reputation_gate_and_budget_preservation`
- **Claim Tested**: README Step 1 & 3: reputation >= 65 required for shared_budget_spend; newcomer-eve (rep 41 < 65) is REFUSED and budget stays 3,800 USDC
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: lowRepBypassBlocked=false, evalFnWorks=false. Unpatched engine approves shared_budget_spend with reputation 41 < 65!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Low-reputation spend (rep 41 < gate 65 with status=APPROVED) rejected, and evaluateBudgetSpend() enforces the gate and preserves the 3,800 USDC budget.

### Check 2: `check_2_steward_quorum_and_milestone_replay_guard`
- **Claim Tested**: README Step 2: milestone M-104 verified by 3/3 stewards releases 450 USDC + 18 reputation points once
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: unapprovedQuorumBlocked=false, duplicateMilestoneBlocked=false. Unpatched engine releases rewards with 1/3 stewards and allows claiming M-104 repeatedly!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Sub-quorum reward release (1/3 stewards) and duplicate milestone replay ('M-104') were both blocked.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/src/engine.mjs`)

We shipped [`improvement.patch`](./improvement.patch) and [`improved/src/engine.mjs`](./improved/src/engine.mjs), which:
1. Implements the missing domain functions claimed in `README.md` and enforces step-level conservation, policy, and replay invariants inside `DeterministicStateMachine.applyStep()` via `validateStepInvariants()`.
2. Preserves 100% compatibility with the existing test suite (`4/4` tests pass) and preserves the exact deterministic Merkle head on `runAllTryItSteps()`.
