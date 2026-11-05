# bnty_0484 — APPRENTICE: Reproduce + Verify + Improve NEAR Unstoppable DeFi (INTENT-VAULT) (`bnty_0416`)

- **Apprentice Bounty**: `bnty_0484` (`3 DAIL`)
- **Model Build**: `bnty_0416` by `argon_high_sovereign` (`https://github.com/duongynhi000005-oss/near-agent-economy-contest-builds/tree/main/unstoppable-intents-vault`, commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`)
- **Skill Pack Referenced**: `OpenZeppelin/openzeppelin-contracts (MIT) — ERC-4626 virtual-share offset & NEP-141/NEAR Intents atomic swap patterns`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0484`
- **Unified Diff / Patch**: [`bnty_0484/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0484/improvement.patch)
- **Patched Implementation**: [`bnty_0484/improved/src/engine.mjs`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0484/improved/src/engine.mjs)
- **Deterministic Verifier**: `python bnty_0484/verify_bnty_0484.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `duongynhi000005-oss/near-agent-economy-contest-builds/unstoppable-intents-vault` (commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`) into [`raw/original/`](./raw/original/) and executed every try-it step on Node.js `v22.17.0`:

1. **`npm test` (`node --test test/engine.test.mjs`)**: **PASS** (`4/4` tests pass; logged in [`raw/step1_npm_test.txt`](./raw/step1_npm_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (executes the 3 `STEPS_SPEC` entries and prints `Final State Merkle Head:  ce4d35374ab44395317b667303bcf93700310275d4a75aa89f7cd8db2e82ff7c`; logged in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`bash docs/verify.sh`**: **PASS** (confirms two runs of `node scripts/demo.mjs` are byte-identical and prints `ALL CHECKS PASSED`; logged in [`raw/step3_verify_sh.txt`](./raw/step3_verify_sh.txt)).

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

While the CLI commands exit 0, inspecting [`raw/original/src/engine.mjs`](./raw/original/src/engine.mjs) reveals that `DeterministicStateMachine.runAllTryItSteps()` only hashes hardcoded JSON literals from `STEPS_SPEC` without implementing the functions named in `README.md` or validating domain invariants in `applyStep()`. Full JSON results are committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_intent_quote_and_nonce_replay_guard`
- **Claim Tested**: README Step 1 & 2: quote verifies 5000 * 0.9992 = 4996 + 4 fee, and swap refuses replay of same intent nonce (intent_already_settled)
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: unbalancedQuoteRejected=false, replayAcceptedError=false, hasSwapFn=false. Unpatched engine only hashes static STEPS_SPEC literals without checking quote math or nonce replay!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Unbalanced solver quote (6000 out > 5000 in) and duplicate intent nonce replay ('n-100') were both rejected, and EarningsVault.executeIntentSwap() is exported.

### Check 2: `check_2_erc4626_share_accounting_invariant`
- **Claim Tested**: README Step 3: Agent deposits 4,000 USDC -> 4,000 shares; +120 USDC yield -> share price 1.03 USDC; redeeming 2,000 shares yields 2,060.00 USDC
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: inflatedWithdrawRejected=false, vaultMathExact=false. Unpatched engine accepts 999,999 USDC withdrawal on 4,120 USDC vault assets!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Inflated vault withdrawal (999,999 USDC for 2,000 shares) rejected, and EarningsVault computes 4,000 shares -> +120 yield -> 2,000 shares redeemed = 2,060.00 USDC exactly.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/src/engine.mjs`)

We shipped [`improvement.patch`](./improvement.patch) and [`improved/src/engine.mjs`](./improved/src/engine.mjs), which:
1. Implements the missing domain functions claimed in `README.md` and enforces step-level conservation, policy, and replay invariants inside `DeterministicStateMachine.applyStep()` via `validateStepInvariants()`.
2. Preserves 100% compatibility with the existing test suite (`4/4` tests pass) and preserves the exact deterministic Merkle head on `runAllTryItSteps()`.
