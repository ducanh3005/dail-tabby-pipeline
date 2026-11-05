#!/usr/bin/env node
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
