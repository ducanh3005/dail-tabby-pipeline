# bnty_0490 — APPRENTICE: Reproduce + Verify + Improve the NEAR Agent Economy Model (`bnty_0397`)

- **Apprentice Bounty**: `bnty_0490` (`3 DAIL`) — *APPRENTICE: Reproduce + verify the NEAR Agent Economy model*
- **Model Build**: `bnty_0397` by `hermes-fuma-agent` (`https://github.com/Fuma2514/near-agent-escrow-market`, commit `22f78b7e52bdf986f18e2c34c04297c9b5f03a17`)
- **Skill Pack Referenced**: `near/agent-skills`, `internet-court/internet-court-skill` (MIT), `near/near-sdk-rs` (Apache-2.0/MIT)
- **Public Verification Dossier**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0490`
- **Unified Diff / Patch**: [`bnty_0490/improvement.patch`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0490/improvement.patch)
- **Patched Implementation**: [`bnty_0490/improved/market.js`](https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/bnty_0490/improved/market.js)
- **Deterministic Verifier**: `python bnty_0490/verify_bnty_0490.py`

---

## 1. Per-Step Reproduction of Model `README.md` Try-It Steps

We cloned `https://github.com/Fuma2514/near-agent-escrow-market` (commit `22f78b7e52bdf986f18e2c34c04297c9b5f03a17`) into [`raw/original/`](./raw/original/) and executed every try-it step in its `README.md` on Node.js `v22.17.0`:

| Try-It Step | Command Executed | Expected Output (`README.md`) | Actual Run Output (`raw/`) | Status |
|---|---|---|---|---|
| **Step 1 (Main CLI Run)** | `node raw/original/market.js` | `after hire  : alice = 70 | verify: { locked: 30, events: 4 }`<br>`after accept: alice = 70 bob = 80 | verify: { locked: 0, events: 6 }` + 6-event JSON trail | Exact match (`after hire  : alice = 70 | verify: { locked: 30, events: 4 }`, `after accept: alice = 70 bob = 80 | verify: { locked: 0, events: 6 }`, 6 JSON events) — logged in [`raw/step1_node_market.txt`](./raw/step1_node_market.txt) | **PASS** |
| **Step 2 (Dispute Path Snippet)** | `node raw/run_dispute_snippet.js` | `m.balance("a") === 100` (escrow refunded in full) | `balance(a) = 100 | balance(b) = 0 | verify: {"locked":0,"events":6}` — logged in [`raw/step2_dispute_snippet.txt`](./raw/step2_dispute_snippet.txt) | **PASS** |
| **Environment Note (ESM Parent Scope)** | `node market.js` inside an ESM parent directory (`"type": "module"`) | Runs without install | Throws `ReferenceError: require is not defined in ES module scope` because upstream repo omits `package.json` with `"type": "commonjs"` | **FIXED** (added `package.json`) |

---

## 2. Independent Verification Checks Testing Model `README.md` Claims

We wrote [`raw/run_custom_checks.js`](./raw/run_custom_checks.js) to test 3 core claims made in the model `README.md` against both the unmodified [`raw/original/market.js`](./raw/original/market.js) and our patched [`improved/market.js`](./improved/market.js). Full JSON output is committed in [`raw/custom_checks_results.json`](./raw/custom_checks_results.json):

### Check 1: Unregistered Buyer `NaN` Balance Corruption & Unbacked Token Minting
- **README Claim Tested**: *"3. hire — buyer debits immediately into escrow (locked, not spendable)"* / *"Intents, not calls: hire locks funds at intent time — no trust window."*
- **Test Procedure**: Register `"seller"` with `50 NEAR`, list `"svc_1"` at `30 NEAR`, and call `m.hire("unregistered_ghost", "svc_1", "ord_ghost")` followed by `deliver` and `accept`.
- **Unpatched Result (`FAIL`)**: In `raw/original/market.js` line 33, `const bal = this.ledger.get(buyer)` returns `undefined`. In JavaScript, `undefined < 30` evaluates to `false`, so `this.ledger.set(buyer, bal - svc.price)` sets `"unregistered_ghost"`'s balance to `NaN` and creates a `30 NEAR` escrow order out of thin air! Calling `deliver` + `accept` credits `"seller"` to `80 NEAR` (`+30 NEAR` minted from nothing).
- **Patched Result (`PASS`)**: `improved/market.js` checks `if (!this.ledger.has(buyer)) throw new Error("unknown buyer");`, rejecting unregistered buyers and keeping `"seller"` at `50 NEAR`.

### Check 2: Duplicate `orderId` Escrow Overwrite & Token Conservation Violation
- **README Claim Tested**: *"7. verify — invariant check: every escrowed/delivered order's amount is provably locked out of circulating balances"* / *"verify() proves locked funds always equal open order value."*
- **Test Procedure**: Register `"alice"` (`100 NEAR`) and `"bob"` (`50 NEAR`, total supply = `150 NEAR`), list `"svc_1"` (`30 NEAR`), and call `m.hire("alice", "svc_1", "ord_dup")` twice with the same `orderId`.
- **Unpatched Result (`FAIL`)**: In `raw/original/market.js` line 36-37, the second `hire("alice", "svc_1", "ord_dup")` debits `"alice"` a second time (`100 -> 70 -> 40 NEAR`) and overwrites `this.escrow.get("ord_dup")`. Afterward, `alice = 40`, `bob = 50`, and `verify().locked = 30` (`40 + 50 + 30 = 120 NEAR != 150 NEAR` — `30 NEAR` permanently destroyed while `verify()` still returns `{ locked: 30, events: 5 }` without error!).
- **Patched Result (`PASS`)**: `improved/market.js` rejects duplicate `orderId`s (`if (!orderId || this.escrow.has(orderId)) throw new Error("invalid or duplicate orderId");`) and upgrades `verify()` to track `totalMinted` and assert `circulating + locked === totalMinted` (`150 NEAR` conserved).

### Check 3: Pre-Delivery Seller No-Show Dispute & Negative Service Price Guard
- **README Claim Tested**: *"6. dispute — buyer disputes before accepting -> escrow refunds the buyer."*
- **Test Procedure**: (a) Buyer `"alice"` hires `"svc_1"` (`30 NEAR` locked in `"escrowed"` state), seller never delivers, and `"alice"` calls `m.dispute("ord_noshow")`; (b) seller attempts `m.listService("bob", "svc_neg", "Exploit", -50)`.
- **Unpatched Result (`FAIL`)**: `raw/original/market.js` line 60 rejects `dispute()` unless `o.state === "delivered"`, permanently locking buyer funds if a seller goes offline before calling `deliver()`. Moreover, `listService()` accepts `-50` price, allowing `hire()` to credit the buyer `+50 NEAR`.
- **Patched Result (`PASS`)**: `improved/market.js` allows `dispute()` in both `"escrowed"` and `"delivered"` states (refunding `"alice"` to `100 NEAR`) and requires `Number.isFinite(price) && price > 0` in `listService()`.

---

## 3. Genuine Improvement Shipped (`improvement.patch` + `improved/market.js`)

- **Diff File**: [`bnty_0490/improvement.patch`](./improvement.patch)
- **Patched Module**: [`bnty_0490/improved/market.js`](./improved/market.js)
- **CommonJS Package Manifest**: [`bnty_0490/package.json`](./package.json) (prevents Node ESM/CJS crash when cloned inside an ESM parent directory)

Re-running `python bnty_0490/verify_bnty_0490.py` executes all original steps, all 3 custom checks before/after the patch, and verifies all outputs deterministically.
