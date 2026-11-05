export async function runSuite(dirLabel, modState, modEngine) {
  const checks = [];

  // Check 1: Does applySwapAction allow a trader with 0 USDC to swap 500,000 USDC into negative balance and mint buyback fees?
  const state1 = modState.createState({ cast: modState.createCast() });
  const brokeTrader = 'acc_broke_trader';
  state1.balances[brokeTrader] = 0;
  state1.usdc[brokeTrader] = 0;
  let overdraftBlocked = false;
  try {
    modEngine.applySwapAction(state1, { trader: brokeTrader, dir: 'y_to_x', amountIn: 500000 });
  } catch (e) {
    overdraftBlocked = true;
  }
  const traderUsdcAfter = state1.usdc[brokeTrader];
  const traderTokensAfter = state1.balances[brokeTrader];
  const pass1 = (overdraftBlocked && traderUsdcAfter === 0 && traderTokensAfter === 0);
  checks.push({
    id: 'check_1_amm_swap_trader_solvency_guard',
    claim_tested: 'README & src/mechanics.js: trader pays USDC/tokens into the AMM pool; unbacked overdraft swaps are rejected',
    passed: pass1,
    overdraft_blocked: overdraftBlocked,
    trader_usdc_after: traderUsdcAfter,
    trader_tokens_after: traderTokensAfter,
    detail: pass1
      ? 'PASS: Unfunded swap of 500,000 USDC by a 0-USDC trader was rejected.'
      : `FAIL: Unfunded trader swapped 500,000 USDC with 0 balance! traderUsdcAfter=${traderUsdcAfter}, traderTokensAfter=${traderTokensAfter}.`
  });

  // Check 2: Does applySwapAction block negative/zero amountIn and pool-draining swaps that drive pool.y negative?
  const state2 = modState.createState({ cast: modState.createCast() });
  const whale = Object.keys(state2.balances).find((a) => state2.balances[a] === 5000000);
  let negAmountBlocked = false;
  try {
    modEngine.applySwapAction(state2, { trader: whale, dir: 'y_to_x', amountIn: -1000 });
  } catch (e) {
    negAmountBlocked = true;
  }
  let poolDrainBlocked = false;
  try {
    // Because quoteSwap inverted pool.x and pool.y in x_to_y: out = (pool.x * netIn) / (pool.y + netIn),
    // selling 500,000 tokens outputs 1,111,111.11 USDC from a 400,000 USDC pool, driving pool.y to -711,111.11!
    modEngine.applySwapAction(state2, { trader: whale, dir: 'x_to_y', amountIn: 500000 });
  } catch (e) {
    poolDrainBlocked = true;
  }
  const poolY = state2.pool.y;
  const pass2 = (negAmountBlocked && poolDrainBlocked && poolY > 0);
  checks.push({
    id: 'check_2_negative_swap_and_pool_reserve_underflow_guard',
    claim_tested: 'README & src/mechanics.js: constant-product AMM reserves stay strictly positive and reject negative swap inputs',
    passed: pass2,
    negative_amount_blocked: negAmountBlocked,
    pool_underflow_blocked: poolDrainBlocked,
    pool_y_reserve_after: poolY,
    detail: pass2
      ? `PASS: Negative swap input and pool-underflow x_to_y swap were both rejected; pool.y reserve remained positive (${poolY}).`
      : `FAIL: negAmountBlocked=${negAmountBlocked}, poolDrainBlocked=${poolDrainBlocked}, pool.y=${poolY} (x_to_y swap of 500k tokens output 1.11M USDC from a 400k USDC pool, driving pool.y negative!).`
  });

  return { label: dirLabel, checks };
}

import * as oState from './original/src/state.js';
import * as oEngine from './original/src/engine.js';
import * as iState from '../improved/src/state.js';
import * as iEngine from '../improved/src/engine.js';

const origRes = await runSuite('original', oState, oEngine);
const impRes = await runSuite('improved', iState, iEngine);
console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
