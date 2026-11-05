export async function runSuite(dirLabel, modState, modEngine) {
  const checks = [];

  // Check 1: Does fundEscrow record escrow.payer so refundEscrow refunds the actual payer, and enforce amount === escrow.amount?
  const state1 = modState.createState();
  const echo = modEngine.resolveAgent(state1, 'client-echo').address;
  const ava = modEngine.resolveAgent(state1, 'agent-ava').address;
  const bob = modEngine.resolveAgent(state1, 'agent-bob').address;

  const esc = modEngine.openEscrow(state1, {
    creator: echo,
    beneficiary: ava,
    amount: 300,
    categories: ['settlement'],
    timestamp: 1000,
  });
  let underfundBlocked = false;
  try {
    modEngine.fundEscrow(state1, { escrowId: esc.id, payer: bob, amount: 1, timestamp: 1005 });
  } catch (e) {
    underfundBlocked = true;
  }

  const state1b = modState.createState();
  const echoB = modEngine.resolveAgent(state1b, 'client-echo').address;
  const avaB = modEngine.resolveAgent(state1b, 'agent-ava').address;
  const bobB = modEngine.resolveAgent(state1b, 'agent-bob').address;
  const escB = modEngine.openEscrow(state1b, {
    creator: echoB,
    beneficiary: avaB,
    amount: 300,
    categories: ['settlement'],
    timestamp: 1000,
  });
  // bobB funds the escrow opened by echoB, then it is refunded
  modEngine.fundEscrow(state1b, { escrowId: escB.id, payer: bobB, amount: 300, timestamp: 1005 });
  modEngine.refundEscrow(state1b, { escrowId: escB.id, reason: 'cancelled', timestamp: 1010 });
  const bobCreditsAfter = state1b.agents[bobB].credits;
  const echoCreditsAfter = state1b.agents[echoB].credits;
  const pass1 = (underfundBlocked && bobCreditsAfter === 1000 && echoCreditsAfter === 1000);
  checks.push({
    id: 'check_1_escrow_payer_refund_and_exact_funding_guard',
    claim_tested: 'README & src/escrow.js: fundEscrow locks the agreed escrow amount and refundEscrow returns funds to the actual payer',
    passed: pass1,
    underfund_blocked: underfundBlocked,
    payer_bob_credits_after_refund: bobCreditsAfter,
    creator_echo_credits_after_refund: echoCreditsAfter,
    detail: pass1
      ? 'PASS: 1-credit underfunding of 300-credit escrow rejected, and refundEscrow returned all 300 credits to payer bob (1000).'
      : `FAIL: underfundBlocked=${underfundBlocked}; fundEscrow forgot to set escrow.payer, so refundEscrow sent bob's 300 credits to creator echo (bob=${bobCreditsAfter}, echo=${echoCreditsAfter})!`
  });

  // Check 2: Does passportOf(state, agent, asOf) exclude future-dated attestations (issuedAt > asOf)?
  const state2 = modState.createState();
  const cid = modEngine.resolveAgent(state2, 'agent-cid').address;
  const reg = state2.registry;
  const attFuture = modEngine.makeAttestation({
    subject: cid,
    issuer: reg,
    category: 'settlement',
    claim: 'future work at t=500000',
    value: 0.95,
    weight: 1.0,
    issuedAt: 500000,
    source: { file: 'synthetic', recordHash: '0'.repeat(64) },
  });
  modEngine.importAttestation(state2, attFuture);
  const historicalPassport = modEngine.passportOf(state2, cid, 100000);
  const settlementScoreAt100k = historicalPassport.scores.settlement.score;
  const pass2 = (settlementScoreAt100k === 0);
  checks.push({
    id: 'check_2_historical_asof_future_attestation_leak_guard',
    claim_tested: 'README & src/score.js: passport lookup at timestamp asOf evaluates only attestations issued at or before asOf',
    passed: pass2,
    settlement_score_at_100k_from_500k_attestation: settlementScoreAt100k,
    detail: pass2
      ? 'PASS: Historical passport lookup at t=100,000 excluded future-dated attestation (issuedAt=500,000).'
      : `FAIL: decayFactor clamped negative age to 0, granting future attestation (issuedAt=500,000) a full score of ${settlementScoreAt100k} at historical t=100,000!`
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
