
async function runSuite(modPath, label) {
  const mod = await import(modPath);
  const { DeterministicStateMachine } = mod;
  const checks = [];

  // Check 1: Does engine enforce human max COGS policy (cogs_ratio_bps <= max_cogs_bps) and inventory arithmetic?
  let check1Pass = false;
  let check1Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let badInventoryBlocked = false;
    try {
      sm.applyStep('sale', { summary: 'bad inv', metrics: { qty: 10, gross_usdc: 1000, inventory_before: 15, inventory_after: 99 } });
    } catch (e) {
      badInventoryBlocked = true;
    }
    let cogsBreachBlocked = false;
    try {
      sm.applyStep('procurement', {
        summary: 'breach cogs',
        metrics: { reorder_point: 6, procured_units: 20, unit_cost_usdc: 30, total_cogs_usdc: 600, cogs_ratio_bps: 6000, max_cogs_bps: 4500, inventory_after: 25, operating_cash_usdc: 1400 }
      });
    } catch (e) {
      cogsBreachBlocked = true;
    }
    check1Pass = badInventoryBlocked && cogsBreachBlocked;
    check1Detail = check1Pass
      ? "PASS: Inventory conservation error (15 - 10 != 99) and COGS policy breach (6000 bps > 4500 bps max) were both rejected."
      : `FAIL: badInventoryBlocked=${badInventoryBlocked}, cogsBreachBlocked=${cogsBreachBlocked}. Unpatched engine accepts COGS ratio 60% > 45% human max without error!`;
  } catch (e) {
    check1Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_1_inventory_and_max_cogs_policy_guard",
    claim_tested: "README Step 1, Step 2 & Sec 3: inventory 15 -> 5 on 10-unit sale, and assert!(cogs_bps <= policy.max_cogs_bps) blocks COGS > 45%",
    passed: check1Pass,
    detail: check1Detail
  });

  // Check 2: Does closeEpoch() enforce the 1,000 USDC reserve floor and 70/20/10 treasury split?
  let check2Pass = false;
  let check2Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let badSplitBlocked = false;
    try {
      sm.applyStep('treasury_split', {
        summary: 'bad split',
        metrics: { reserve_floor_usdc: 1000, distributable_profit_usdc: 640, owner_vault_usdc: 600, growth_pool_usdc: 100, gas_buffer_usdc: 100 }
      });
    } catch (e) {
      badSplitBlocked = true;
    }
    let closeEpochWorks = false;
    if (typeof mod.closeEpoch === 'function') {
      const res = mod.closeEpoch({ operatingCashUsdc: 1640, reserveFloorUsdc: 1000 });
      closeEpochWorks = (res.distributable_profit_usdc === 640 && res.owner_vault_usdc === 448 && res.growth_pool_usdc === 128 && res.gas_buffer_usdc === 64);
    }
    check2Pass = badSplitBlocked && closeEpochWorks;
    check2Detail = check2Pass
      ? "PASS: Unbalanced treasury split (600+100+100 != 640) rejected, and closeEpoch(1640, 1000) computes 448/128/64 (70%/20%/10%) exactly."
      : `FAIL: badSplitBlocked=${badSplitBlocked}, closeEpochWorks=${closeEpochWorks}. Unpatched engine has no closeEpoch() function and accepts invalid splits!`;
  } catch (e) {
    check2Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_2_close_epoch_reserve_floor_and_70_20_10_split",
    claim_tested: "README Step 3: closeEpoch() enforces 1,000 USDC reserve floor and splits 640 USDC profit 70% (448) / 20% (128) / 10% (64)",
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
