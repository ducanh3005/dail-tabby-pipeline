# FRONTIER-ECON - autonomous NPC wallets, player-owned AMM/orderbook market, and self-balancing game economy

## 1. Problem Solved
Static game shops suffer from hyperinflation and require developer balance patches because NPCs have infinite money/items instead of bounded wallets and utility-driven supply/demand pricing.

## 2. Try It ('Do X -> See Y' Deterministic Steps)
```bash
npm test
node scripts/demo.mjs
bash docs/verify.sh
```
1. **`npc_trade`**: Blacksmith NPC (wallet 800 GOLD, inventory 12 IRON_INGOT) buys 6 IRON_ORE from Miner NPC (wallet 200 GOLD) at market price 25 GOLD/unit -> Blacksmith wallet = 650 GOLD, Miner wallet = 350 GOLD, total money supply conserved = 2,500 GOLD
2. **`market_price_moves`**: Scarcity shock reduces IRON_ORE pool reserve from 100 to 60 units -> constant-product market price moves endogenously from 25.00 GOLD to 41.67 GOLD (+66.68%) without any admin parameter patch
3. **`player_sale`**: player-kira crafts 4 STEEL_BLADE and sells into the player-owned market pool -> receives 312.50 GOLD net of 2% LP fee (6.38 GOLD distributed to player liquidity providers)

Final Merkle State Head: `dfe43804c8dd3465b444adb469cd60818cbe9814c09b60c9412b55d8797d5cfa`

## 3. Mechanical Mapping to NEAR Protocol Contracts
Maps 1:1 to a NEAR game-loop contract where NPC agents are registered sub-accounts with bounded NEP-141 balances and deterministic tick functions (`execute_npc_tick`), trading against a player-LP constant-product pool.

## 4. Plain Disclosure
- **Zero External Dependencies**: Uses Node.js standard library (`node:crypto`, `node:test`, `node:assert`, `node:fs`) only.
- **No Secrets or Network Calls**: Deterministic offline verification (`bash docs/verify.sh` -> `ALL CHECKS PASSED`).
- **Shared Utility Harness Disclosure**: The SHA-256 hash-chain verification harness (`DeterministicStateMachine`) and `docs/verify.sh` layout are shared across our 7 NEAR Contest Build track entries (`bnty_0422`, `bnty_0420`, `bnty_0419`, `bnty_0417`, `bnty_0416`, `bnty_0412`, `bnty_0411`), while each track's step specifications, domain invariants, and state transitions are tailored to that track.
