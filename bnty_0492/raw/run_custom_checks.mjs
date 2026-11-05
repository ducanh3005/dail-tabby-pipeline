
async function runSuite(modPath, label) {
  const mod = await import(modPath);
  const { DeterministicStateMachine } = mod;
  const checks = [];

  // Check 1: Does engine enforce bounded NPC wallets and total GOLD supply conservation (2,500 GOLD)?
  let check1Pass = false;
  let check1Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let inflationBlocked = false;
    try {
      sm.applyStep('npc_trade', {
        summary: 'infinite gold exploit',
        metrics: { buyer_npc: 'blacksmith.npc.near', seller_npc: 'miner.npc.near', item: 'IRON_ORE', qty: 6, unit_price_gold: 25, blacksmith_gold_after: 800, miner_gold_after: 950, total_supply_gold: 9999 }
      });
    } catch (e) {
      inflationBlocked = true;
    }
    let npcTradeFnWorks = false;
    if (typeof mod.executeNpcTrade === 'function') {
      const r = mod.executeNpcTrade({ buyerGoldBefore: 800, sellerGoldBefore: 200, qty: 6, unitPriceGold: 25 });
      npcTradeFnWorks = (r.blacksmith_gold_after === 650 && r.miner_gold_after === 350 && r.total_supply_gold === 2500);
    }
    check1Pass = inflationBlocked && npcTradeFnWorks;
    check1Detail = check1Pass
      ? "PASS: Unconserved NPC trade (total_supply_gold=9999) rejected, and executeNpcTrade() conserves 650 + 350 + 1500 = 2,500 GOLD."
      : `FAIL: inflationBlocked=${inflationBlocked}, npcTradeFnWorks=${npcTradeFnWorks}. Unpatched engine allows arbitrary NPC gold minting!`;
  } catch (e) {
    check1Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_1_npc_wallet_solvency_and_gold_conservation",
    claim_tested: "README Step 1: Blacksmith (800 GOLD) buys 6 IRON_ORE from Miner (200 GOLD) @ 25 GOLD -> 650 / 350 GOLD, total supply conserved = 2,500 GOLD",
    passed: check1Pass,
    detail: check1Detail
  });

  // Check 2: Does engine validate pool reserve shock pricing and the 2% player LP fee?
  let check2Pass = false;
  let check2Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let badFeeBlocked = false;
    try {
      sm.applyStep('player_sale', {
        summary: 'wrong lp fee',
        metrics: { player: 'player-kira.near', item: 'STEEL_BLADE', qty: 4, net_payout_gold: 312.5, lp_fee_gold: 50.0 }
      });
    } catch (e) {
      badFeeBlocked = true;
    }
    let priceFnWorks = false;
    if (typeof mod.computeMarketShockPrice === 'function') {
      const p = mod.computeMarketShockPrice({ oreReserveBefore: 100, oreReserveAfter: 60, priceBeforeGold: 25.0 });
      priceFnWorks = (p.constant_gold_reserve_price === 41.67 && p.constant_product_swap_price === 69.44 && p.pct_change === 66.68);
    }
    check2Pass = badFeeBlocked && priceFnWorks;
    check2Detail = check2Pass
      ? "PASS: Invalid LP fee (50 GOLD on 312.5 net != 2%) rejected, and computeMarketShockPrice() verifies both constant-gold-reserve shock price (41.67 GOLD, +66.68%) and constant-product swap price (69.44 GOLD)."
      : `FAIL: badFeeBlocked=${badFeeBlocked}, priceFnWorks=${priceFnWorks}. Unpatched engine has no pricing or LP fee validation!`;
  } catch (e) {
    check2Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_2_pool_shock_pricing_and_2pct_lp_fee_guard",
    claim_tested: "README Step 2 & 3: reserve shock 100 -> 60 moves price 25.00 -> 41.67 GOLD (+66.68%), and player sale deducts 2% LP fee (6.38 GOLD on 318.88 gross)",
    passed: check2Pass,
    detail: check2Detail
  });

  return { label, checks };
}

import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const origUrl = pathToFileURL(path.join(__dirname, 'original', 'src', 'engine.mjs')).href;
const impUrl = pathToFileURL(path.join(__dirname, '..', 'improved', 'src', 'engine.mjs')).href;

const origRes = await runSuite(origUrl, 'original_engine_mjs');
const impRes = await runSuite(impUrl, 'improved_engine_mjs');
console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
