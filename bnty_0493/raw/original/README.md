# VAULT-NFT - NEP-171 token-bound account NFTs that own money, split royalties, hold inventory, and present credentials

## 1. Problem Solved
Standard NFTs are passive metadata pointers; agents and creators need NFTs that act as autonomous sub-accounts holding fungible balances, enforcing multi-recipient royalty splits on every cashflow, storing equipment inventory, and signing verifiable access credentials.

## 2. Try It ('Do X -> See Y' Deterministic Steps)
```bash
npm test
node scripts/demo.mjs
bash docs/verify.sh
```
1. **`nft_receives_funds`**: Token #42 (vault-42.nft.near) receives 2,000 USDC gross revenue -> 90% (1,800 USDC) credited to NFT account balance, 10% (200 USDC) reserved in royalty pool
2. **`pays_royalty`**: distributeRoyalties(#42) splits the 200 USDC royalty pool -> creator-ava receives 140 USDC (70%), co-author-ben receives 60 USDC (30%); royalty pool = 0 USDC
3. **`presents_credential`**: Token #42 holds inventory ['rig-mk3', 'dataset-v2'] and signs SHA-256 access credential `tier:pro-validator` -> verifyCredential() returns ok=true; after transfer to buyer-cara, old owner's credential presentation returns ok=false (signer_not_current_owner)

Final Merkle State Head: `ffe959b7c9742c916e226835b7328bb7564a32e9dbb5d4a96cdc6c1c59395a07`

## 3. Mechanical Mapping to NEAR Protocol Contracts
Maps 1:1 to NEP-171 (Core NFT) + NEP-199 (Royalties) + Token-Bound Subaccount (`nft-<id>.<contract>.near`) on NEAR where each token ID controls an internal balance map, inventory set, and credential attestation registry.

## 4. Plain Disclosure
- **Zero External Dependencies**: Uses Node.js standard library (`node:crypto`, `node:test`, `node:assert`, `node:fs`) only.
- **No Secrets or Network Calls**: Deterministic offline verification (`bash docs/verify.sh` -> `ALL CHECKS PASSED`).
- **Shared Utility Harness Disclosure**: The SHA-256 hash-chain verification harness (`DeterministicStateMachine`) and `docs/verify.sh` layout are shared across our 7 NEAR Contest Build track entries (`bnty_0422`, `bnty_0420`, `bnty_0419`, `bnty_0417`, `bnty_0416`, `bnty_0412`, `bnty_0411`), while each track's step specifications, domain invariants, and state transitions are tailored to that track.
