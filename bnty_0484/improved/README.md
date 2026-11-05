# INTENT-VAULT - non-custodial cross-chain NEAR Intents solver swap and ERC-4626-style agent earnings vault

## 1. Problem Solved
Trading and service agents earning across multiple chains need a non-custodial way to quote and settle cross-chain swaps via NEAR Intents and park idle USDC earnings into a yield-accruing share vault without custodian risk.

## 2. Try It ('Do X -> See Y' Deterministic Steps)
```bash
npm test
node scripts/demo.mjs
bash docs/verify.sh
```
1. **`quote`**: Solver quotes cross-chain intent swap of 5,000 Base USDC (`eip155:8453`) -> NEAR USDC (`near:mainnet`) at 0.9992 rate (4,996.00 NEAR USDC, 4.00 USDC solver fee, 300s deadline, signed intent hash verified)
2. **`swap`**: executeIntentSwap() verifies solver + user commitments and settles atomically -> agent NEAR balance = 4,996.00 USDC, solver balance +4.00 USDC, replay of same intent nonce -> REFUSED (intent_already_settled)
3. **`deposit_and_withdraw`**: Agent deposits 4,000.00 USDC into EarningsVault -> receives 4,000.0000 vUSDC shares; after 120.00 USDC protocol revenue accrues to the vault (share price = 1.0300 USDC), agent redeems 2,000.0000 shares -> receives 2,060.00 USDC exactly

Final Merkle State Head: `ce4d35374ab44395317b667303bcf93700310275d4a75aa89f7cd8db2e82ff7c`

## 3. Mechanical Mapping to NEAR Protocol Contracts
Maps 1:1 to NEAR Intents (`intents.near` `execute_intents` multi-token diff verification) paired with a NEP-141 share-accounting vault contract (`deposit` / `withdraw` with virtual share offset preventing inflation attacks).

## 4. Plain Disclosure
- **Zero External Dependencies**: Uses Node.js standard library (`node:crypto`, `node:test`, `node:assert`, `node:fs`) only.
- **No Secrets or Network Calls**: Deterministic offline verification (`bash docs/verify.sh` -> `ALL CHECKS PASSED`).
- **Shared Utility Harness Disclosure**: The SHA-256 hash-chain verification harness (`DeterministicStateMachine`) and `docs/verify.sh` layout are shared across our 7 NEAR Contest Build track entries (`bnty_0422`, `bnty_0420`, `bnty_0419`, `bnty_0417`, `bnty_0416`, `bnty_0412`, `bnty_0411`), while each track's step specifications, domain invariants, and state transitions are tailored to that track.
