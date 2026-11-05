export async function runSuite(dirLabel, modState, modEngine, modAsset) {
  const checks = [];

  // Check 1: Does a second subscribe() wipe out 6 months of unaccrued yield on existing units?
  const state1 = modState.createState();
  const issuer = state1.issuer;
  const avery = state1.partyOrder.find((a) => state1.parties[a].name === 'fund-avery');
  modEngine.clearParty(state1, { admin: issuer, address: avery, status: 'VERIFIED', jurisdiction: 'US', timestamp: 1000 });
  modEngine.registerAsset(state1, {
    admin: issuer,
    id: 'tbill-test',
    name: 'US T-Bill',
    kind: 'treasury',
    totalSupply: 1_000_000,
    maturity: 1000 + 31536000,
    yieldBps: 500, // 5% APY
    timestamp: 1000,
  });
  // Subscribe 100,000 units at t = 1000
  modEngine.subscribeAction(state1, { investor: avery, assetId: 'tbill-test', amount: 100000, timestamp: 1000 });
  // Half a year later (t = 1000 + 15768000), subscribe 100 more units before calling accrueAction
  const halfYear = 1000 + 15768000;
  modEngine.subscribeAction(state1, { investor: avery, assetId: 'tbill-test', amount: 100, timestamp: halfYear });
  modEngine.accrueAction(state1, { assetId: 'tbill-test', timestamp: halfYear });
  const holder1 = state1.assets['tbill-test'].holders[avery];
  const pass1 = (holder1.accrued === 2500);
  checks.push({
    id: 'check_1_pre_subscribe_yield_preservation',
    claim_tested: 'README & src/asset.js: yield builds up on the face value a holder has held (100,000 units @ 5% APY for 0.5 yr = 2,500 USDC)',
    passed: pass1,
    accrued_usdc: holder1.accrued,
    expected_usdc: 2500,
    detail: pass1
      ? 'PASS: Subscribing 100 additional units at 0.5 yr preserved the 2,500 USDC accrued yield on the initial 100,000 units.'
      : `FAIL: Second subscribe() overwrote holder.lastAccrual = timestamp without accruing first, wiping out 2,500 USDC of yield (accrued=${holder1.accrued})!`
  });

  // Check 2: Can a transfer signature be replayed at the same timestamp to double-drain seller units?
  const state2 = modState.createState();
  const issuer2 = state2.issuer;
  const avery2 = state2.partyOrder.find((a) => state2.parties[a].name === 'fund-avery');
  const birch2 = state2.partyOrder.find((a) => state2.parties[a].name === 'fund-birch');
  modEngine.clearParty(state2, { admin: issuer2, address: avery2, status: 'VERIFIED', jurisdiction: 'US', timestamp: 1000 });
  modEngine.clearParty(state2, { admin: issuer2, address: birch2, status: 'VERIFIED', jurisdiction: 'TW', timestamp: 1000 });
  modEngine.registerAsset(state2, {
    admin: issuer2,
    id: 'tbill-replay',
    name: 'US T-Bill',
    kind: 'treasury',
    totalSupply: 1_000_000,
    maturity: 1000 + 31536000,
    yieldBps: 500,
    timestamp: 1000,
  });
  modEngine.subscribeAction(state2, { investor: avery2, assetId: 'tbill-replay', amount: 20000, timestamp: 1000 });
  const sig = modEngine.signTransfer(state2, avery2, { to: birch2, assetId: 'tbill-replay', units: 10000, timestamp: 2000 });
  modEngine.transferAction(state2, { from: avery2, to: birch2, assetId: 'tbill-replay', units: 10000, timestamp: 2000, signature: sig });
  let replayBlocked = false;
  try {
    modEngine.transferAction(state2, { from: avery2, to: birch2, assetId: 'tbill-replay', units: 10000, timestamp: 2000, signature: sig });
  } catch (e) {
    replayBlocked = true;
  }
  const averyRemaining = state2.assets['tbill-replay'].holders[avery2].units;
  const pass2 = (replayBlocked && averyRemaining === 10000);
  checks.push({
    id: 'check_2_transfer_signature_replay_guard',
    claim_tested: 'README & src/asset.js: a transfer signature cannot be replayed into another transfer',
    passed: pass2,
    replay_blocked: replayBlocked,
    seller_units_remaining: averyRemaining,
    detail: pass2
      ? 'PASS: Replaying the identical transfer signature was rejected; seller retained 10,000 units.'
      : `FAIL: Replaying the identical transfer signature drained all 20,000 units from seller (remaining=${averyRemaining})!`
  });

  return { label: dirLabel, checks };
}

import * as oState from './original/src/state.js';
import * as oEngine from './original/src/engine.js';
import * as oAsset from './original/src/asset.js';
import * as iState from '../improved/src/state.js';
import * as iEngine from '../improved/src/engine.js';
import * as iAsset from '../improved/src/asset.js';

const origRes = await runSuite('original', oState, oEngine, oAsset);
const impRes = await runSuite('improved', iState, iEngine, iAsset);
console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
