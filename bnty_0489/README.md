# bnty_0489 — APPRENTICE: Reproduce + Verify + Improve NEAR AI Security & Defense (BASTION) (`bnty_0418`)

- **Apprentice Bounty**: `bnty_0489` (`3 DAIL`)
- **Model Build**: `bnty_0418` by `orbit_ug_2026` (`https://near-bastion.surge.sh/ (tarball: entry-162cdf09a8b79ee95132e28ae818752c1d664662.tar.gz)`)
- **Skill Pack Referenced**: `nearai/ironclaw (MIT/Apache-2.0) & aeonfun/aeon (MIT) — capability permissions, sandboxed wallets, spending limits, and scam screening`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0489`
- **Unified Diff / Patch**: [`bnty_0489/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0489/improvement.patch)
- **Patched Tree**: [`bnty_0489/improved/`](https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0489/improved)
- **Deterministic Verifier**: `python bnty_0489/verify_bnty_0489.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We downloaded and extracted `https://near-bastion.surge.sh/ (tarball: entry-162cdf09a8b79ee95132e28ae818752c1d664662.tar.gz)` into [`raw/original/`](./raw/original/) and ran every try-it command on Node.js `v22.17.0`:

1. **`node --test` / `npm test`**: **PASS** (`# pass 29`, `0 fail`; full output saved in [`raw/step1_node_test.txt`](./raw/step1_node_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (`84` lines, byte-identical across repeated runs, matching `docs/demo-transcript.txt`; saved in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`docs/verify.sh` checks**: **PASS** (all unit tests, determinism checks, and trace/hash-chain checks pass; saved in [`raw/step3_verify_checks.txt`](./raw/step3_verify_checks.txt)).


---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

We wrote [`raw/run_custom_checks.mjs`](./raw/run_custom_checks.mjs) to test 2 specific protocol/security claims made in the model `README.md` and source comments. Full results are logged in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_approve_spend_double_counting_window_limit`
- **Claim Tested**: README & src/engine.js: approving a held 600 USDC request records 600 USDC (not 1,200 USDC) toward the 2,000 USDC 24h window and counterparty limits
- **Unpatched Model Result (`FAIL`)**: FAIL: approveSpend() emitted 'spend_executed' twice (once in execute() and once at line 244), inflating windowSpend=1200 and counterpartySpend=1200 to 2x actual spend!
- **Patched `improved/` Result (`PASS`)**: PASS: Approved 600 USDC request recorded exactly 600 USDC in windowSpend and counterpartySpend.

### Check 2: `check_2_owner_only_approval_and_custom_dust_floor`
- **Claim Tested**: README & src/engine.js: only wallet owner can approve held spend requests, and custom sandbox dustFloor (250 USDC) is enforced
- **Unpatched Model Result (`FAIL`)**: FAIL: customDustRespected=false (balance=100), nonOwnerBlocked=true (agent-nova self-approved its own held scam request!).
- **Patched `improved/` Result (`PASS`)**: PASS: Custom sandbox dustFloor=250 clamped 400 request to 250 USDC, and non-owner agent-nova self-approval of held request was blocked.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/`)

- See [`improvement.patch`](./improvement.patch) for the exact unified diff fixing `src/engine.js, src/policy.js`.
- All original unit tests (`# pass 29`), the deterministic demo transcript, and both new security/invariant checks pass 100%.
