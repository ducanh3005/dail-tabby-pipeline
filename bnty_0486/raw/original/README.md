# BLIND-ESCROW - confidential agent job escrow with shielded payment commitments, private computation attestation, and atomic reveal

## 1. Problem Solved
Public onchain escrows leak proprietary prompts, dataset contents, and bilateral pricing to competitors; agents need confidential escrow where job inputs stay encrypted, payment is locked behind a cryptographic commitment, and funds release atomically upon verified output reveal.

## 2. Try It ('Do X -> See Y' Deterministic Steps)
```bash
npm test
node scripts/demo.mjs
bash docs/verify.sh
```
1. **`private_job`**: Buyer posts confidential job #701 with encrypted payload hash `sha256(ciphertext)` and viewing-key commitment; plaintext prompt never touches public state (public observer sees only commitment hash)
2. **`shielded_payment`**: Buyer locks 750 USDC in shielded commitment note `C = H(amount || blinding_factor || job_id)` -> escrow pool reserve increases by 750 USDC; forged commitment with wrong blinding factor -> REFUSED
3. **`completion_reveal`**: Worker submits enclave execution proof + encrypted result commitment; atomicReveal() verifies proof against job #701, releases 750 USDC to worker note, and reveals the decryption key to buyer (`decrypted_ok: true`)

Final Merkle State Head: `6b9970a5ac9b71c47b8ac6166fcbe7b06cbe499a12f8e1cde2f646f8306484b4`

## 3. Mechanical Mapping to NEAR Protocol Contracts
Maps 1:1 to a NEAR confidential escrow contract combining NEP-141 shielded pool notes (commitment/nullifier trees) with TEE/zk attestation verification (`verify_attestation_and_settle`).

## 4. Plain Disclosure
- **Zero External Dependencies**: Uses Node.js standard library (`node:crypto`, `node:test`, `node:assert`, `node:fs`) only.
- **No Secrets or Network Calls**: Deterministic offline verification (`bash docs/verify.sh` -> `ALL CHECKS PASSED`).
- **Shared Utility Harness Disclosure**: The SHA-256 hash-chain verification harness (`DeterministicStateMachine`) and `docs/verify.sh` layout are shared across our 7 NEAR Contest Build track entries (`bnty_0422`, `bnty_0420`, `bnty_0419`, `bnty_0417`, `bnty_0416`, `bnty_0412`, `bnty_0411`), while each track's step specifications, domain invariants, and state transitions are tailored to that track.
