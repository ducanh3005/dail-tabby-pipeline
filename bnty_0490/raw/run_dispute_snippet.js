const { EscrowMarket } = require("./original/market.js");
const m = new EscrowMarket();
m.register("a", 100); m.register("b", 0);
m.listService("b", "s1", "x", 40);
const o = m.hire("a", "s1", "o1");
m.deliver(o);
m.dispute(o);                       // refund path
console.log("balance(a) =", m.balance("a"), "| balance(b) =", m.balance("b"), "| verify:", JSON.stringify(m.verify()));
