# TREZU-SOCIAL - shared budgets, programmable rewards, and reputation-gated access on Sputnik DAO / Trezu

## 1. Problem Solved
DAO multisigs approve raw transfers but lack epoch-bounded shared department budgets, deterministic contributor reward streams, and category-level reputation gates that block low-reputation spenders without rebuilding the underlying Sputnik DAO multisig.

## 2. Try It ('Do X -> See Y' Deterministic Steps)
```bash
npm test
node scripts/demo.mjs
bash docs/verify.sh
```
1. **`shared_budget_spend`**: ops-alice spends 1,200 USDC from the 5,000 USDC Q4 Growth shared budget (reputation 82 >= gate 65) -> APPROVED; remaining epoch budget = 3,800 USDC, multisig vault balance = 48,800 USDC
2. **`reward_payout`**: milestone M-104 verified by 3/3 stewards -> programmable reward engine releases 450 USDC + 18 reputation points to builder-bob -> balance = 450 USDC, reputation = 78
3. **`reputation_gate`**: newcomer-eve (reputation 41 < gate 65) attempts 500 USDC shared budget spend -> REFUSED (reputation_below_minimum: 41 < 65); budget unchanged at 3,800 USDC

Final Merkle State Head: `665465ae2267e2ccb52b116e34f32d43990cdfbe21997bfb5ae62487f2e01826`

## 3. Mechanical Mapping to NEAR Protocol Contracts
Maps 1:1 to a Sputnik DAO v2 policy extension contract on NEAR (`#[near(contract_state)]`): `SharedBudget` -> `LookupMap<BudgetId, EpochBudget>`, `spend_from_budget()` -> cross-contract call `ext_sputnik::act_proposal` gated by `assert!(rep >= budget.min_reputation)`, and `claim_reward()` -> NEP-141 `ft_transfer`.

## 4. Plain Disclosure
- **Zero External Dependencies**: Uses Node.js standard library (`node:crypto`, `node:test`, `node:assert`, `node:fs`) only.
- **No Secrets or Network Calls**: Deterministic offline verification (`bash docs/verify.sh` -> `ALL CHECKS PASSED`).
- **Shared Utility Harness Disclosure**: The SHA-256 hash-chain verification harness (`DeterministicStateMachine`) and `docs/verify.sh` layout are shared across our 7 NEAR Contest Build track entries (`bnty_0422`, `bnty_0420`, `bnty_0419`, `bnty_0417`, `bnty_0416`, `bnty_0412`, `bnty_0411`), while each track's step specifications, domain invariants, and state transitions are tailored to that track.
