# bnty_0492 — APPRENTICE: Reproduce + Verify + Improve NEAR Games With Real Economies (FRONTIER-ECON) (`bnty_0419`)

- **Apprentice Bounty**: `bnty_0492` (`3 DAIL`)
- **Model Build**: `bnty_0419` by `argon_high_sovereign` (`https://github.com/duongynhi000005-oss/near-agent-economy-contest-builds/tree/main/autonomous-npc-economy`, commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`)
- **Skill Pack Referenced**: `latticexyz/mud (MIT) — autonomous ECS world state, bounded NPC wallets, and AMM/pool pricing`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0492`
- **Unified Diff / Patch**: [`bnty_0492/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0492/improvement.patch)
- **Patched Implementation**: [`bnty_0492/improved/src/engine.mjs`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0492/improved/src/engine.mjs)
- **Deterministic Verifier**: `python bnty_0492/verify_bnty_0492.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `duongynhi000005-oss/near-agent-economy-contest-builds/autonomous-npc-economy` (commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`) into [`raw/original/`](./raw/original/) and executed every try-it step on Node.js `v22.17.0`:

1. **`npm test` (`node --test test/engine.test.mjs`)**: **PASS** (`4/4` tests pass; logged in [`raw/step1_npm_test.txt`](./raw/step1_npm_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (executes the 3 `STEPS_SPEC` entries and prints `Final State Merkle Head:  dfe43804c8dd3465b444adb469cd60818cbe9814c09b60c9412b55d8797d5cfa`; logged in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`bash docs/verify.sh`**: **PASS** (confirms two runs of `node scripts/demo.mjs` are byte-identical and prints `ALL CHECKS PASSED`; logged in [`raw/step3_verify_sh.txt`](./raw/step3_verify_sh.txt)).

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

While the CLI commands exit 0, inspecting [`raw/original/src/engine.mjs`](./raw/original/src/engine.mjs) reveals that `DeterministicStateMachine.runAllTryItSteps()` only hashes hardcoded JSON literals from `STEPS_SPEC` without implementing the functions named in `README.md` or validating domain invariants in `applyStep()`. Full JSON results are committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_npc_wallet_solvency_and_gold_conservation`
- **Claim Tested**: README Step 1: Blacksmith (800 GOLD) buys 6 IRON_ORE from Miner (200 GOLD) @ 25 GOLD -> 650 / 350 GOLD, total supply conserved = 2,500 GOLD
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: inflationBlocked=false, npcTradeFnWorks=false. Unpatched engine allows arbitrary NPC gold minting!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Unconserved NPC trade (total_supply_gold=9999) rejected, and executeNpcTrade() conserves 650 + 350 + 1500 = 2,500 GOLD.

### Check 2: `check_2_pool_shock_pricing_and_2pct_lp_fee_guard`
- **Claim Tested**: README Step 2 & 3: reserve shock 100 -> 60 moves price 25.00 -> 41.67 GOLD (+66.68%), and player sale deducts 2% LP fee (6.38 GOLD on 318.88 gross)
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: badFeeBlocked=false, priceFnWorks=false. Unpatched engine has no pricing or LP fee validation!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Invalid LP fee (50 GOLD on 312.5 net != 2%) rejected, and computeMarketShockPrice() verifies both constant-gold-reserve shock price (41.67 GOLD, +66.68%) and constant-product swap price (69.44 GOLD).

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/src/engine.mjs`)

We shipped [`improvement.patch`](./improvement.patch) and [`improved/src/engine.mjs`](./improved/src/engine.mjs), which:
1. Implements the missing domain functions claimed in `README.md` and enforces step-level conservation, policy, and replay invariants inside `DeterministicStateMachine.applyStep()` via `validateStepInvariants()`.
2. Preserves 100% compatibility with the existing test suite (`4/4` tests pass) and preserves the exact deterministic Merkle head on `runAllTryItSteps()`.
