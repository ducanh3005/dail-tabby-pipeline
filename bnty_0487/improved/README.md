# INTENT-SHOP - AI-native autonomous merchant with NEAR Intents cross-chain checkout, auto-procurement, and policy-constrained treasury split

## 1. Problem Solved
AI merchant agents need to sell services across chains via NEAR Intents, automatically restock upstream compute/data inventory when stock drops below a threshold, and split net profit under strict human-configured safety rails (max COGS ratio and reserve floor).

## 2. Try It ('Do X -> See Y' Deterministic Steps)
```bash
npm test
node scripts/demo.mjs
bash docs/verify.sh
```
1. **`sale`**: Customer settles cross-chain NEAR Intent (`eip155:8453:USDC -> near:USDC`, 1,000 USDC) for 10 API-Audit packs -> order fulfilled, gross revenue = 1,000 USDC, inventory 15 -> 5 units
2. **`procurement`**: Inventory (5) <= reorder point (6) triggers autonomous procurement of 20 upstream units at 18 USDC/unit (360 USDC total, COGS ratio 36% <= human max 45%) -> inventory = 25 units, operating cash = 1,640 USDC
3. **`treasury_split`**: closeEpoch() enforces 1,000 USDC reserve floor and splits 640 USDC distributable profit -> 70% (448 USDC) to human owner vault, 20% (128 USDC) to growth pool, 10% (64 USDC) to agent compute gas buffer

Final Merkle State Head: `a622619842c55e35a6d0a14278e1029580302fdeacd8d274713d761c43aaea4a`

## 3. Mechanical Mapping to NEAR Protocol Contracts
Maps 1:1 to a NEAR Intents (`verifier.near`) receiver contract implementing `mt_on_transfer`, automated solver procurement intents, and human-governed constraint checks (`assert!(cogs_bps <= policy.max_cogs_bps)`).

## 4. Plain Disclosure
- **Zero External Dependencies**: Uses Node.js standard library (`node:crypto`, `node:test`, `node:assert`, `node:fs`) only.
- **No Secrets or Network Calls**: Deterministic offline verification (`bash docs/verify.sh` -> `ALL CHECKS PASSED`).
- **Shared Utility Harness Disclosure**: The SHA-256 hash-chain verification harness (`DeterministicStateMachine`) and `docs/verify.sh` layout are shared across our 7 NEAR Contest Build track entries (`bnty_0422`, `bnty_0420`, `bnty_0419`, `bnty_0417`, `bnty_0416`, `bnty_0412`, `bnty_0411`), while each track's step specifications, domain invariants, and state transitions are tailored to that track.
