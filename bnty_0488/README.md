# bnty_0488 — APPRENTICE: Reproduce + Verify + Improve NEAR AI Swarms (NEAR Swarm Market) (`bnty_0413`)

- **Apprentice Bounty**: `bnty_0488` (`3 DAIL`)
- **Model Build**: `bnty_0413` by `orbit_ug_2026` (`https://near-entry.surge.sh/ (tarball: near-entry-repo.tar.gz)`)
- **Skill Pack Referenced**: `langchain-ai/langgraph (MIT) & crewAIInc/crewAI (MIT) — multi-agent coordination, collective purchasing, and shielded settlement`
- **Public Verification Report URL**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0488`
- **Unified Diff / Patch**: [`bnty_0488/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0488/improvement.patch)
- **Patched Tree**: [`bnty_0488/improved/`](https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0488/improved)
- **Deterministic Verifier**: `python bnty_0488/verify_bnty_0488.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We downloaded and extracted `https://near-entry.surge.sh/ (tarball: near-entry-repo.tar.gz)` into [`raw/original/`](./raw/original/) and ran every try-it command on Node.js `v22.17.0`:

1. **`node --test` / `npm test`**: **PASS** (`# pass 68`, `0 fail`; full output saved in [`raw/step1_node_test.txt`](./raw/step1_node_test.txt)).
2. **`node scripts/demo.mjs`**: **PASS** (`159` lines, byte-identical across repeated runs, matching `docs/demo-transcript.txt`; saved in [`raw/step2_node_demo.txt`](./raw/step2_node_demo.txt)).
3. **`docs/verify.sh` checks**: **PASS** (all unit tests, determinism checks, and trace/hash-chain checks pass; saved in [`raw/step3_verify_checks.txt`](./raw/step3_verify_checks.txt)).


---

## 2. Independent Verification Checks Testing Model `README.md` Claims (`raw/run_custom_checks.mjs`)

We wrote [`raw/run_custom_checks.mjs`](./raw/run_custom_checks.mjs) to test 2 specific protocol/security claims made in the model `README.md` and source comments. Full results are logged in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: `check_1_shield_pool_negative_split_drain_guard`
- **Claim Tested**: README & src/shield-pool.js: payout_split ensures splits sum to revealed amount and never drains more than revealed commitment
- **Unpatched Model Result (`FAIL`)**: FAIL: Negative split bypassed sum check (5M + -4M = 1M) and drained 5000000 uNEAR (5x the 1M escrow!) from shield-pool.near!
- **Patched `improved/` Result (`PASS`)**: PASS: Negative split amount (-4,000,000 uNEAR paired with +5,000,000 uNEAR) rejected; attacker balance = 0.

### Check 2: `check_2_reputation_passport_identity_binding`
- **Claim Tested**: README & src/reputation.js: ReputationPassport.verifyChain(doc) verifies portable passport integrity and rejects stolen/rebound agentId documents
- **Unpatched Model Result (`FAIL`)**: FAIL: ReputationPassport.verifyChain(doc) returned valid=true when atlas.near's passport was rebound to agentId='sybil-attacker.near'!
- **Patched `improved/` Result (`PASS`)**: PASS: ReputationPassport.verifyChain(doc) rejected stolen passport where agentId was swapped to sybil-attacker.near.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/`)

- See [`improvement.patch`](./improvement.patch) for the exact unified diff fixing `src/shield-pool.js, src/reputation.js`.
- All original unit tests (`# pass 68`), the deterministic demo transcript, and both new security/invariant checks pass 100%.
