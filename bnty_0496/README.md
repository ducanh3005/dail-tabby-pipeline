# bnty_0496 — APPRENTICE: Reproduce + Verify + Improve NEAR Open Innovation (PASSPORT) (`bnty_0415`)

- **Apprentice Bounty**: `bnty_0496` (`3 DAIL`)
- **Model Build**: `bnty_0415` by `orbit_ug_2026` (`https://near-passport.surge.sh/ (tarball: entry-d95c602881619ab640ff322459e9b9175fc62e01.tar.gz)`)
- **Skill Pack Referenced**: `a2aproject/A2A (Apache-2.0) & MarimerLLC/agentregistry (MIT) — portable agent reputation passport, category gates, and escrow history`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0496`
- **Unified Diff / Patch**: [`bnty_0496/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0496/improvement.patch)
- **Patched Tree**: [`bnty_0496/improved/`](https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0496/improved)
- **Deterministic Verifier**: `python bnty_0496/verify_bnty_0496.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We downloaded and extracted `https://near-passport.surge.sh/ (tarball: entry-d95c602881619ab640ff322459e9b9175fc62e01.tar.gz)` into [`raw/original/`](./raw/original/) and ran every try-it command on Node.js `v22.17.0`:

1. **`node --test` / `npm test`**: **PASS** (`# pass 26`, `0 fail`; full output saved in [`raw/step1_node_test.txt`](./raw/step1_node_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (`51` lines, byte-identical across repeated runs, matching `docs/demo-transcript.txt`; saved in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`docs/verify.sh` checks**: **PASS** (all unit tests, determinism checks, and trace/hash-chain checks pass; saved in [`raw/step3_verify_checks.txt`](./raw/step3_verify_checks.txt)).


---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

We wrote [`raw/run_custom_checks.mjs`](./raw/run_custom_checks.mjs) to test 2 specific protocol/security claims made in the model `README.md` and source comments. Full results are logged in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_escrow_payer_refund_and_exact_funding_guard`
- **Claim Tested**: README & src/escrow.js: fundEscrow locks the agreed escrow amount and refundEscrow returns funds to the actual payer
- **Unpatched Model Result (`FAIL`)**: FAIL: underfundBlocked=false; fundEscrow forgot to set escrow.payer, so refundEscrow sent bob's 300 credits to creator echo (bob=700, echo=1300)!
- **Patched `improved/` Result (`PASS`)**: PASS: 1-credit underfunding of 300-credit escrow rejected, and refundEscrow returned all 300 credits to payer bob (1000).

### Check 2: `check_2_historical_asof_future_attestation_leak_guard`
- **Claim Tested**: README & src/score.js: passport lookup at timestamp asOf evaluates only attestations issued at or before asOf
- **Unpatched Model Result (`FAIL`)**: FAIL: decayFactor clamped negative age to 0, granting future attestation (issuedAt=500,000) a full score of 95 at historical t=100,000!
- **Patched `improved/` Result (`PASS`)**: PASS: Historical passport lookup at t=100,000 excluded future-dated attestation (issuedAt=500,000).

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/`)

- See [`improvement.patch`](./improvement.patch) for the exact unified diff fixing `src/escrow.js, src/score.js`.
- All original unit tests (`# pass 26`), the deterministic demo transcript, and both new security/invariant checks pass 100%.
