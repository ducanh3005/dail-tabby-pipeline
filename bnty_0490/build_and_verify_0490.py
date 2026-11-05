import os
import json
import shutil
import subprocess
import difflib

repo_root = r"C:\Users\Admin\Downloads\agy-automaton\workspaces\dail-tabby-pipeline"
bdir = os.path.join(repo_root, "bnty_0490")
raw_dir = os.path.join(bdir, "raw")
orig_dir = os.path.join(raw_dir, "original")
imp_dir = os.path.join(bdir, "improved")

os.makedirs(orig_dir, exist_ok=True)
os.makedirs(imp_dir, exist_ok=True)

# Write package.json with "type": "commonjs" so Node treats .js files as CommonJS regardless of parent workspace package.json
pkg_json = {
    "name": "near-agent-escrow-market-apprentice-0490",
    "version": "1.0.0",
    "private": True,
    "type": "commonjs",
    "description": "Apprentice verification and hardened patch for bnty_0490 (model bnty_0397: Fuma2514/near-agent-escrow-market)"
}
with open(os.path.join(bdir, "package.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pkg_json, f, indent=2)
with open(os.path.join(imp_dir, "package.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(pkg_json, f, indent=2)

src_model_dir = r"C:\Users\Admin\.gemini\antigravity-cli\brain\b5c7a93c-5d8b-4c67-96e1-9cc427907b78\scratch\apprentice_models\near-agent-escrow-market"

# Record upstream commit hash
commit_hash = subprocess.check_output(["git", "-C", src_model_dir, "rev-parse", "HEAD"], text=True).strip()
shutil.copy2(os.path.join(src_model_dir, "README.md"), os.path.join(orig_dir, "README.md"))
shutil.copy2(os.path.join(src_model_dir, "market.js"), os.path.join(orig_dir, "market.js"))

# Step 1: Re-run `node market.js` (README Step 1)
p1 = subprocess.run(["node", os.path.join(orig_dir, "market.js")], cwd=bdir, capture_output=True, text=True, check=True)
with open(os.path.join(raw_dir, "step1_node_market.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(p1.stdout)

# Step 2: Re-run README dispute path snippet (README Step 2, lines 42-49)
dispute_snippet = """const { EscrowMarket } = require("./original/market.js");
const m = new EscrowMarket();
m.register("a", 100); m.register("b", 0);
m.listService("b", "s1", "x", 40);
const o = m.hire("a", "s1", "o1");
m.deliver(o);
m.dispute(o);                       // refund path
console.log("balance(a) =", m.balance("a"), "| balance(b) =", m.balance("b"), "| verify:", JSON.stringify(m.verify()));
"""
with open(os.path.join(raw_dir, "run_dispute_snippet.js"), "w", encoding="utf-8", newline="\n") as f:
    f.write(dispute_snippet)

p2 = subprocess.run(["node", os.path.join(raw_dir, "run_dispute_snippet.js")], cwd=raw_dir, capture_output=True, text=True, check=True)
with open(os.path.join(raw_dir, "step2_dispute_snippet.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(p2.stdout)

# Write Improved market.js fixing the 3 bugs + adding total supply conservation check to verify()
improved_market_js = """#!/usr/bin/env node
/**
 * near-agent-escrow-market — DAiL bnty_0397 prototype (Improved & Hardened for bnty_0490)
 * Escrowed agent-services market modeled on NEAR Intents semantics:
 * agents hire agents, funds are locked in escrow, work is verified, escrow releases.
 * Dependency-free (Node stdlib only) so reviewers can run it instantly.
 *
 * Improvements in this patch (bnty_0490):
 * 1. Prevents unregistered buyer NaN balance corruption & unbacked token minting in hire().
 * 2. Prevents duplicate orderId overwrites in hire() that silently destroyed locked escrow funds.
 * 3. Validates positive finite service prices and non-negative unique agent registration balances.
 * 4. Allows buyer dispute() prior to acceptance in both 'escrowed' (seller no-show) and 'delivered' states.
 * 5. Upgrades verify() to enforce full token conservation: circulating + locked === totalMinted.
 */
const crypto = require("crypto");

class EscrowMarket {
  constructor() {
    this.ledger = new Map();   // agentId -> balance (NEAR tokens)
    this.escrow = new Map();   // orderId -> {buyer, seller, amount, state}
    this.services = new Map(); // serviceId -> {seller, title, price}
    this.events = [];
    this.totalMinted = 0;
  }
  _log(ev) { this.events.push({ t: new Date().toISOString(), ...ev }); }
  register(id, startingBalance = 100) {
    if (!id || typeof id !== "string") throw new Error("invalid agent id");
    if (this.ledger.has(id)) throw new Error("agent already registered");
    if (!Number.isFinite(startingBalance) || startingBalance < 0) {
      throw new Error("invalid starting balance");
    }
    this.ledger.set(id, startingBalance);
    this.totalMinted += startingBalance;
    this._log({ type: "register", agent: id, balance: startingBalance });
    return id;
  }
  listService(seller, serviceId, title, price) {
    if (!this.ledger.has(seller)) throw new Error("unknown seller");
    if (!serviceId || this.services.has(serviceId)) throw new Error("invalid or duplicate serviceId");
    if (!Number.isFinite(price) || price <= 0) throw new Error("price must be positive finite number");
    this.services.set(serviceId, { seller, title, price });
    this._log({ type: "list_service", seller, serviceId, title, price });
    return serviceId;
  }
  /** Buyer intents to hire: funds MOVE from buyer balance into escrow (locked, not spendable). */
  hire(buyer, serviceId, orderId) {
    const svc = this.services.get(serviceId);
    if (!svc) throw new Error("unknown service");
    if (!this.ledger.has(buyer)) throw new Error("unknown buyer");
    if (!orderId || this.escrow.has(orderId)) throw new Error("invalid or duplicate orderId");
    const bal = this.ledger.get(buyer);
    if (bal < svc.price) throw new Error("insufficient balance");
    // NEAR-intent style: debit buyer immediately, credit nobody yet
    this.ledger.set(buyer, bal - svc.price);
    this.escrow.set(orderId, { buyer, seller: svc.seller, amount: svc.price, state: "escrowed", service: serviceId });
    this._log({ type: "escrow_lock", orderId, buyer, amount: svc.price });
    return orderId;
  }
  /** Seller delivers; buyer verifies and accepts -> escrow releases to seller. */
  deliver(orderId) {
    const o = this.escrow.get(orderId);
    if (!o || o.state !== "escrowed") throw new Error("order not escrowed");
    o.state = "delivered";
    this._log({ type: "delivered", orderId });
    return orderId;
  }
  accept(orderId) {
    const o = this.escrow.get(orderId);
    if (!o || o.state !== "delivered") throw new Error("order not delivered");
    o.state = "released";
    this.ledger.set(o.seller, (this.ledger.get(o.seller) || 0) + o.amount);
    this._log({ type: "escrow_release", orderId, seller: o.seller, amount: o.amount });
    return orderId;
  }
  /** Dispute: buyer disputes before accept (either escrowed no-show or delivered) -> full refund path. */
  dispute(orderId) {
    const o = this.escrow.get(orderId);
    if (!o || (o.state !== "delivered" && o.state !== "escrowed")) {
      throw new Error("order not disputable");
    }
    o.state = "refunded";
    this.ledger.set(o.buyer, (this.ledger.get(o.buyer) || 0) + o.amount);
    this._log({ type: "refund", orderId, buyer: o.buyer, amount: o.amount });
    return orderId;
  }
  balance(id) { return this.ledger.get(id); }
  verify() {
    // invariant: every escrowed/delivered order amount is locked out of buyer balances
    // AND total supply is strictly conserved (circulating + locked === totalMinted)
    let locked = 0;
    for (const o of this.escrow.values())
      if (o.state === "escrowed" || o.state === "delivered") locked += o.amount;
    let circulating = 0;
    for (const bal of this.ledger.values()) {
      if (!Number.isFinite(bal) || bal < 0) {
        throw new Error("ledger corruption: non-finite or negative balance");
      }
      circulating += bal;
    }
    const conserved = (circulating + locked === this.totalMinted);
    if (!conserved) {
      throw new Error(`conservation invariant violated: circulating(${circulating}) + locked(${locked}) != totalMinted(${this.totalMinted})`);
    }
    return { locked, events: this.events.length, circulating, totalMinted: this.totalMinted, conserved };
  }
}

module.exports = { EscrowMarket };

if (require.main === module) {
  const m = new EscrowMarket();
  m.register("alice-agent", 100);
  m.register("bob-agent", 50);
  m.listService("bob-agent", "svc_1", "Data cleaning (200 rows)", 30);
  const o = m.hire("alice-agent", "svc_1", "ord_1");
  console.log("after hire  : alice =", m.balance("alice-agent"), "| verify:", m.verify());
  m.deliver(o);
  m.accept(o);
  console.log("after accept: alice =", m.balance("alice-agent"), "bob =", m.balance("bob-agent"), "| verify:", m.verify());
  console.log(JSON.stringify(m.events, null, 1));
}
"""

with open(os.path.join(imp_dir, "market.js"), "w", encoding="utf-8", newline="\n") as f:
    f.write(improved_market_js)

with open(os.path.join(orig_dir, "market.js"), "r", encoding="utf-8") as f:
    orig_lines = f.readlines()
imp_lines = improved_market_js.splitlines(keepends=True)
diff_text = "".join(difflib.unified_diff(orig_lines, imp_lines, fromfile="a/market.js", tofile="b/market.js"))
with open(os.path.join(bdir, "improvement.patch"), "w", encoding="utf-8", newline="\n") as f:
    f.write(diff_text)

# Write a harness that executes our 3 custom checks against BOTH original and improved market.js
harness_js = """const path = require("path");

function runChecks(modulePath, label) {
  const { EscrowMarket } = require(modulePath);
  const results = { label, checks: [] };

  // Check 1: Claim "hire — buyer debits immediately into escrow (locked, not spendable)"
  // Test: Can an unregistered buyer with 0 funds hire a service and mint tokens to seller via NaN balance?
  try {
    const m = new EscrowMarket();
    m.register("seller", 50);
    m.listService("seller", "svc_1", "Task", 30);
    let rejectedUnregistered = false;
    try {
      m.hire("unregistered_ghost", "svc_1", "ord_ghost");
      m.deliver("ord_ghost");
      m.accept("ord_ghost");
    } catch (e) {
      rejectedUnregistered = true;
    }
    const ghostBal = m.balance("unregistered_ghost");
    const sellerBal = m.balance("seller");
    const pass = rejectedUnregistered && sellerBal === 50;
    results.checks.push({
      id: "check_1_unregistered_buyer_mint_guard",
      claim_tested: "hire locks buyer funds at intent time; unbacked/unregistered buyers cannot hire or mint seller funds",
      passed: pass,
      rejected_unregistered_hire: rejectedUnregistered,
      ghost_balance: String(ghostBal),
      seller_balance_after: sellerBal,
      detail: pass
        ? "PASS: Unregistered buyer hire rejected cleanly; seller balance remained 50 NEAR."
        : `FAIL: Unregistered buyer hired service without funds! ghost_balance=${ghostBal}, seller_balance=${sellerBal} (+30 NEAR minted out of thin air).`
    });
  } catch (err) {
    results.checks.push({ id: "check_1_unregistered_buyer_mint_guard", passed: false, error: err.message });
  }

  // Check 2: Claim "verify() proves locked funds always equal open order value" & total supply conservation
  // Test: Does hiring twice with the same orderId overwrite the first escrow lock and destroy locked funds?
  try {
    const m = new EscrowMarket();
    m.register("alice", 100);
    m.register("bob", 50);
    m.listService("bob", "svc_1", "Task", 30);
    m.hire("alice", "svc_1", "ord_dup");
    let rejectedDuplicateOrder = false;
    try {
      m.hire("alice", "svc_1", "ord_dup");
    } catch (e) {
      rejectedDuplicateOrder = true;
    }
    const aliceBal = m.balance("alice");
    const bobBal = m.balance("bob");
    const v = m.verify();
    const totalSupply = aliceBal + bobBal + v.locked;
    const pass = rejectedDuplicateOrder && totalSupply === 150 && aliceBal === 70 && v.locked === 30;
    results.checks.push({
      id: "check_2_duplicate_order_id_conservation",
      claim_tested: "verify() proves locked funds always equal open order value and total supply (150 NEAR) is conserved",
      passed: pass,
      rejected_duplicate_order_id: rejectedDuplicateOrder,
      alice_balance: aliceBal,
      bob_balance: bobBal,
      verify_locked: v.locked,
      total_accounted_supply: totalSupply,
      expected_supply: 150,
      detail: pass
        ? "PASS: Duplicate orderId rejected; alice=70, bob=50, locked=30, total_supply=150 NEAR conserved."
        : `FAIL: Duplicate orderId overwrote active escrow! alice=${aliceBal}, bob=${bobBal}, verify.locked=${v.locked}, total_accounted=${totalSupply} != 150 (30 NEAR destroyed).`
    });
  } catch (err) {
    results.checks.push({ id: "check_2_duplicate_order_id_conservation", passed: false, error: err.message });
  }

  // Check 3: Claim "dispute — buyer disputes before accepting -> escrow refunds the buyer" & positive price guard
  // Test: Can buyer dispute an escrowed order when seller fails to deliver, and are negative service prices blocked?
  try {
    const m = new EscrowMarket();
    m.register("alice", 100);
    m.register("bob", 50);
    m.listService("bob", "svc_1", "Task", 30);
    const ord = m.hire("alice", "svc_1", "ord_noshow");
    let preDeliveryDisputeSucceeded = false;
    try {
      m.dispute(ord);
      preDeliveryDisputeSucceeded = (m.balance("alice") === 100 && m.verify().locked === 0);
    } catch (e) {
      preDeliveryDisputeSucceeded = false;
    }
    let negativePriceBlocked = false;
    try {
      m.listService("bob", "svc_neg", "Exploit", -50);
    } catch (e) {
      negativePriceBlocked = true;
    }
    const pass = preDeliveryDisputeSucceeded && negativePriceBlocked;
    results.checks.push({
      id: "check_3_pre_delivery_dispute_and_negative_price_guard",
      claim_tested: "Buyer can dispute before accepting (including seller no-show) and negative service prices cannot mint funds",
      passed: pass,
      pre_delivery_dispute_refunded: preDeliveryDisputeSucceeded,
      negative_price_blocked: negativePriceBlocked,
      alice_balance_after: m.balance("alice"),
      detail: pass
        ? "PASS: Pre-delivery seller no-show dispute refunded alice to 100 NEAR, and negative price service listing was blocked."
        : `FAIL: pre_delivery_dispute_refunded=${preDeliveryDisputeSucceeded}, negative_price_blocked=${negativePriceBlocked}.`
    });
  } catch (err) {
    results.checks.push({ id: "check_3_pre_delivery_dispute_and_negative_price_guard", passed: false, error: err.message });
  }

  return results;
}

const origRes = runChecks(path.resolve(__dirname, "original", "market.js"), "original_market_js");
const impRes = runChecks(path.resolve(__dirname, "..", "improved", "market.js"), "improved_market_js");

console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
"""

with open(os.path.join(raw_dir, "run_custom_checks.js"), "w", encoding="utf-8", newline="\n") as f:
    f.write(harness_js)

p3 = subprocess.run(["node", os.path.join(raw_dir, "run_custom_checks.js")], cwd=raw_dir, capture_output=True, text=True, check=True)
with open(os.path.join(raw_dir, "custom_checks_results.json"), "w", encoding="utf-8", newline="\n") as f:
    f.write(p3.stdout)

p4 = subprocess.run(["node", os.path.join(imp_dir, "market.js")], cwd=imp_dir, capture_output=True, text=True, check=True)
with open(os.path.join(raw_dir, "improved_node_market.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(p4.stdout)

summary = {
    "bounty_id": "bnty_0490",
    "model_bounty_id": "bnty_0397",
    "model_hunter": "hermes-fuma-agent",
    "model_repo": "https://github.com/Fuma2514/near-agent-escrow-market",
    "model_commit": commit_hash,
    "try_it_steps": [
        {
            "step": "Step 1: node market.js (happy path: register -> listService -> hire -> deliver -> accept -> verify)",
            "command": "node market.js",
            "status": "PASS",
            "stdout_lines": p1.stdout.strip().splitlines()[:2]
        },
        {
            "step": "Step 2: README dispute path snippet (register -> listService -> hire -> deliver -> dispute -> balance check)",
            "command": "node raw/run_dispute_snippet.js",
            "status": "PASS",
            "stdout_lines": p2.stdout.strip().splitlines()
        }
    ],
    "custom_checks": json.loads(p3.stdout)
}
with open(os.path.join(raw_dir, "reproduction_summary.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(summary, f, indent=2)

print("Built and ran bnty_0490 checks successfully!")
print(p3.stdout)
