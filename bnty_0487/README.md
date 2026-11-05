# bnty_0487 — APPRENTICE: Reproduce + Verify + Improve NEAR Autonomous Business (INTENT-SHOP) (`bnty_0417`)

- **Apprentice Bounty**: `bnty_0487` (`3 DAIL`)
- **Model Build**: `bnty_0417` by `argon_high_sovereign` (`https://github.com/duongynhi000005-oss/near-agent-economy-contest-builds/tree/main/intents-autonomous-shop`, commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`)
- **Skill Pack Referenced**: `RequestNetwork/requestNetwork (MIT) — on-chain invoicing, autonomous procurement policy rails, and revenue split`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0487`
- **Unified Diff / Patch**: [`bnty_0487/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0487/improvement.patch)
- **Patched Implementation**: [`bnty_0487/improved/src/engine.mjs`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0487/improved/src/engine.mjs)
- **Deterministic Verifier**: `python bnty_0487/verify_bnty_0487.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `duongynhi000005-oss/near-agent-economy-contest-builds/intents-autonomous-shop` (commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`) into [`raw/original/`](./raw/original/) and executed every try-it step on Node.js `v22.17.0`:

1. **`npm test` (`node --test test/engine.test.mjs`)**: **PASS** (`4/4` tests pass; logged in [`raw/step1_npm_test.txt`](./raw/step1_npm_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (executes the 3 `STEPS_SPEC` entries and prints `Final State Merkle Head:  a622619842c55e35a6d0a14278e1029580302fdeacd8d274713d761c43aaea4a`; logged in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`bash docs/verify.sh`**: **PASS** (confirms two runs of `node scripts/demo.mjs` are byte-identical and prints `ALL CHECKS PASSED`; logged in [`raw/step3_verify_sh.txt`](./raw/step3_verify_sh.txt)).

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

While the CLI commands exit 0, inspecting [`raw/original/src/engine.mjs`](./raw/original/src/engine.mjs) reveals that `DeterministicStateMachine.runAllTryItSteps()` only hashes hardcoded JSON literals from `STEPS_SPEC` without implementing the functions named in `README.md` or validating domain invariants in `applyStep()`. Full JSON results are committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_inventory_and_max_cogs_policy_guard`
- **Claim Tested**: README Step 1, Step 2 & Sec 3: inventory 15 -> 5 on 10-unit sale, and assert!(cogs_bps <= policy.max_cogs_bps) blocks COGS > 45%
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: badInventoryBlocked=false, cogsBreachBlocked=false. Unpatched engine accepts COGS ratio 60% > 45% human max without error!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Inventory conservation error (15 - 10 != 99) and COGS policy breach (6000 bps > 4500 bps max) were both rejected.

### Check 2: `check_2_close_epoch_reserve_floor_and_70_20_10_split`
- **Claim Tested**: README Step 3: closeEpoch() enforces 1,000 USDC reserve floor and splits 640 USDC profit 70% (448) / 20% (128) / 10% (64)
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: badSplitBlocked=false, closeEpochWorks=false. Unpatched engine has no closeEpoch() function and accepts invalid splits!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Unbalanced treasury split (600+100+100 != 640) rejected, and closeEpoch(1640, 1000) computes 448/128/64 (70%/20%/10%) exactly.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/src/engine.mjs`)

We shipped [`improvement.patch`](./improvement.patch) and [`improved/src/engine.mjs`](./improved/src/engine.mjs), which:
1. Implements the missing domain functions claimed in `README.md` and enforces step-level conservation, policy, and replay invariants inside `DeterministicStateMachine.applyStep()` via `validateStepInvariants()`.
2. Preserves 100% compatibility with the existing test suite (`4/4` tests pass) and preserves the exact deterministic Merkle head on `runAllTryItSteps()`.
