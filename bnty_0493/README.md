# bnty_0493 — APPRENTICE: Reproduce + Verify + Improve NEAR NFTs That Do Something (VAULT-NFT) (`bnty_0420`)

- **Apprentice Bounty**: `bnty_0493` (`3 DAIL`)
- **Model Build**: `bnty_0420` by `argon_high_sovereign` (`https://github.com/duongynhi000005-oss/near-agent-economy-contest-builds/tree/main/nep-account-nft`, commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`)
- **Skill Pack Referenced**: `keypom/keypom (GPL-3.0) — NEP-171 token-bound accounts, royalty splits, and owner-gated credential presentation`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0493`
- **Unified Diff / Patch**: [`bnty_0493/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0493/improvement.patch)
- **Patched Implementation**: [`bnty_0493/improved/src/engine.mjs`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0493/improved/src/engine.mjs)
- **Deterministic Verifier**: `python bnty_0493/verify_bnty_0493.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `duongynhi000005-oss/near-agent-economy-contest-builds/nep-account-nft` (commit `5cb1e77cc1b0d6ddfc70abf1d10fbafb7f046258`) into [`raw/original/`](./raw/original/) and executed every try-it step on Node.js `v22.17.0`:

1. **`npm test` (`node --test test/engine.test.mjs`)**: **PASS** (`4/4` tests pass; logged in [`raw/step1_npm_test.txt`](./raw/step1_npm_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (executes the 3 `STEPS_SPEC` entries and prints `Final State Merkle Head:  ffe959b7c9742c916e226835b7328bb7564a32e9dbb5d4a96cdc6c1c59395a07`; logged in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`bash docs/verify.sh`**: **PASS** (confirms two runs of `node scripts/demo.mjs` are byte-identical and prints `ALL CHECKS PASSED`; logged in [`raw/step3_verify_sh.txt`](./raw/step3_verify_sh.txt)).

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

While the CLI commands exit 0, inspecting [`raw/original/src/engine.mjs`](./raw/original/src/engine.mjs) reveals that `DeterministicStateMachine.runAllTryItSteps()` only hashes hardcoded JSON literals from `STEPS_SPEC` without implementing the functions named in `README.md` or validating domain invariants in `applyStep()`. Full JSON results are committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_nft_inflow_and_royalty_split_conservation`
- **Claim Tested**: README Step 1 & 2: 2,000 USDC inflow splits 1,800 treasury / 200 royalty pool, and distributeRoyalties(#42) pays 140 (70%) + 60 (30%)
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: overpayBlocked=false, distFnWorks=false. Unpatched engine has no distributeRoyalties() and accepts 500 USDC payouts from a 200 USDC pool!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Overpaying royalties (500 USDC from 200 USDC pool) rejected, and distributeRoyalties(200) computes 140/60 USDC exactly.

### Check 2: `check_2_nft_owner_transfer_credential_revocation`
- **Claim Tested**: README Step 3: verifyCredential() returns ok=true for current owner and ok=false (signer_not_current_owner) for old owner after transfer
- **Unpatched `src/engine.mjs` Result (`FAIL`)**: FAIL: staleAcceptedBlocked=false, credFnWorks=false. Unpatched engine has no verifyCredential() and accepts stale_owner_verified=true!
- **Patched `improved/src/engine.mjs` Result (`PASS`)**: PASS: Stale owner credential presentation rejected (signer_not_current_owner) in both verifyCredential() and applyStep().

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/src/engine.mjs`)

We shipped [`improvement.patch`](./improvement.patch) and [`improved/src/engine.mjs`](./improved/src/engine.mjs), which:
1. Implements the missing domain functions claimed in `README.md` and enforces step-level conservation, policy, and replay invariants inside `DeterministicStateMachine.applyStep()` via `validateStepInvariants()`.
2. Preserves 100% compatibility with the existing test suite (`4/4` tests pass) and preserves the exact deterministic Merkle head on `runAllTryItSteps()`.
