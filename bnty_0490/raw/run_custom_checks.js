const path = require("path");

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
