# bnty_0491 — APPRENTICE: Reproduce + Verify + Improve NEAR Real-World Money (ANCHOR) (`bnty_0414`)

- **Apprentice Bounty**: `bnty_0491` (`3 DAIL`)
- **Model Build**: `bnty_0414` by `orbit_ug_2026` (`https://near-anchor.surge.sh/ (tarball: entry-060546fe63c4e5e56bcb6ee7be64efb633fdf612.tar.gz)`)
- **Skill Pack Referenced**: `x402-foundation/x402 — tokenised real-world asset registry, double-entry ledger, compliance gate, and yield accrual`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0491`
- **Unified Diff / Patch**: [`bnty_0491/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0491/improvement.patch)
- **Patched Tree**: [`bnty_0491/improved/`](https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0491/improved)
- **Deterministic Verifier**: `python bnty_0491/verify_bnty_0491.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We downloaded and extracted `https://near-anchor.surge.sh/ (tarball: entry-060546fe63c4e5e56bcb6ee7be64efb633fdf612.tar.gz)` into [`raw/original/`](./raw/original/) and ran every try-it command on Node.js `v22.17.0`:

1. **`node --test` / `npm test`**: **PASS** (`# pass 22`, `0 fail`; full output saved in [`raw/step1_node_test.txt`](./raw/step1_node_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (`54` lines, byte-identical across repeated runs, matching `docs/demo-transcript.txt`; saved in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`docs/verify.sh` checks**: **PASS** (all unit tests, determinism checks, and trace/hash-chain checks pass; saved in [`raw/step3_verify_checks.txt`](./raw/step3_verify_checks.txt)).


---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

We wrote [`raw/run_custom_checks.mjs`](./raw/run_custom_checks.mjs) to test 2 specific protocol/security claims made in the model `README.md` and source comments. Full results are logged in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_pre_subscribe_yield_preservation`
- **Claim Tested**: README & src/asset.js: yield builds up on the face value a holder has held (100,000 units @ 5% APY for 0.5 yr = 2,500 USDC)
- **Unpatched Model Result (`FAIL`)**: FAIL: Second subscribe() overwrote holder.lastAccrual = timestamp without accruing first, wiping out 2,500 USDC of yield (accrued=0)!
- **Patched `improved/` Result (`PASS`)**: PASS: Subscribing 100 additional units at 0.5 yr preserved the 2,500 USDC accrued yield on the initial 100,000 units.

### Check 2: `check_2_transfer_signature_replay_guard`
- **Claim Tested**: README & src/asset.js: a transfer signature cannot be replayed into another transfer
- **Unpatched Model Result (`FAIL`)**: FAIL: Replaying the identical transfer signature drained all 20,000 units from seller (remaining=0)!
- **Patched `improved/` Result (`PASS`)**: PASS: Replaying the identical transfer signature was rejected; seller retained 10,000 units.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/`)

- See [`improvement.patch`](./improvement.patch) for the exact unified diff fixing `src/asset.js`.
- All original unit tests (`# pass 22`), the deterministic demo transcript, and both new security/invariant checks pass 100%.
