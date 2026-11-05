# bnty_0494 — APPRENTICE: Reproduce + Verify + Improve NEAR Memecoins With Mechanics (RITUAL) (`bnty_0421`)

- **Apprentice Bounty**: `bnty_0494` (`3 DAIL`)
- **Model Build**: `bnty_0421` by `orbit_ug_2026` (`https://near-ritual.surge.sh/ (tarball: entry-5220181036f1fc1dba015229f368cfde98729860.tar.gz)`)
- **Skill Pack Referenced**: `Model build pattern reference (Ed25519 quorum rituals, treasury floor & buyback rules, constant-product AMM)`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0494`
- **Unified Diff / Patch**: [`bnty_0494/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0494/improvement.patch)
- **Patched Tree**: [`bnty_0494/improved/`](https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0494/improved)
- **Deterministic Verifier**: `python bnty_0494/verify_bnty_0494.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We downloaded and extracted `https://near-ritual.surge.sh/ (tarball: entry-5220181036f1fc1dba015229f368cfde98729860.tar.gz)` into [`raw/original/`](./raw/original/) and ran every try-it command on Node.js `v22.17.0`:

1. **`node --test` / `npm test`**: **PASS** (`# pass 21`, `0 fail`; full output saved in [`raw/step1_node_test.txt`](./raw/step1_node_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (`70` lines, byte-identical across repeated runs, matching `docs/demo-transcript.txt`; saved in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`docs/verify.sh` checks**: **PASS** (all unit tests, determinism checks, and trace/hash-chain checks pass; saved in [`raw/step3_verify_checks.txt`](./raw/step3_verify_checks.txt)).
- **Packaging Defect Note (`bnty_0494`)**: The model submission/README tells reviewers to download `ritual-5220181036f1fc1dba015229f368cfde98729860.tar.gz`, which returns `HTTP 404 Not Found` on `https://near-ritual.surge.sh/`; the actual hosted tarball URL on the site index is `https://near-ritual.surge.sh/entry-5220181036f1fc1dba015229f368cfde98729860.tar.gz`.

---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

We wrote [`raw/run_custom_checks.mjs`](./raw/run_custom_checks.mjs) to test 2 specific protocol/security claims made in the model `README.md` and source comments. Full results are logged in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_amm_swap_trader_solvency_guard`
- **Claim Tested**: README & src/mechanics.js: trader pays USDC/tokens into the AMM pool; unbacked overdraft swaps are rejected
- **Unpatched Model Result (`FAIL`)**: FAIL: Unfunded trader swapped 500,000 USDC with 0 balance! traderUsdcAfter=-500000, traderTokensAfter=79679.67967968.
- **Patched `improved/` Result (`PASS`)**: PASS: Unfunded swap of 500,000 USDC by a 0-USDC trader was rejected.

### Check 2: `check_2_negative_swap_and_pool_reserve_underflow_guard`
- **Claim Tested**: README & src/mechanics.js: constant-product AMM reserves stay strictly positive and reject negative swap inputs
- **Unpatched Model Result (`FAIL`)**: FAIL: negAmountBlocked=false, poolDrainBlocked=false, pool.y=-713446.59874071 (x_to_y swap of 500k tokens output 1.11M USDC from a 400k USDC pool, driving pool.y negative!).
- **Patched `improved/` Result (`PASS`)**: PASS: Negative swap input and pool-underflow x_to_y swap were both rejected; pool.y reserve remained positive (400000).

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/`)

- See [`improvement.patch`](./improvement.patch) for the exact unified diff fixing `src/mechanics.js`.
- All original unit tests (`# pass 21`), the deterministic demo transcript, and both new security/invariant checks pass 100%.
