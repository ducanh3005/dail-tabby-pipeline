export async function runSuite(dirLabel, modShield, modChain, modPriv, modRep) {
  const checks = [];

  // Check 1: ShieldPoolContract.payout_split negative split drain exploit
  const chain = new modChain.LocalChain();
  const pool = new modShield.ShieldPoolContract();
  chain.deployContract(pool);
  chain.getAccount('shield-pool.near').balance = 10_000_000;
  chain.createAccount('attacker.near', 0);
  chain.createAccount('dummy.near', 0);

  const reveal = { amount: 1_000_000, nonce: 'n1', blind: 'b1' };
  const commitment = modPriv.shieldedCommitment(reveal);
  await chain.callFunction({ contractId: 'shield-pool.near', method: 'open_escrow', args: { escrow_id: 'e1', commitment }, signer: 'shield-pool.near' });

  const { result: res } = await chain.callFunction({
    contractId: 'shield-pool.near',
    method: 'payout_split',
    args: {
      escrow_id: 'e1',
      reveal,
      splits: [
        { recipient: 'attacker.near', amount: 5_000_000 },
        { recipient: 'dummy.near', amount: -4_000_000 },
      ],
    },
    signer: 'shield-pool.near',
  });
  const attackerBal = await chain.getBalance('attacker.near');
  const pass1 = (res.ok === false && attackerBal === 0);
  checks.push({
    id: 'check_1_shield_pool_negative_split_drain_guard',
    claim_tested: 'README & src/shield-pool.js: payout_split ensures splits sum to revealed amount and never drains more than revealed commitment',
    passed: pass1,
    attacker_balance_unear: attackerBal,
    detail: pass1
      ? 'PASS: Negative split amount (-4,000,000 uNEAR paired with +5,000,000 uNEAR) rejected; attacker balance = 0.'
      : `FAIL: Negative split bypassed sum check (5M + -4M = 1M) and drained ${attackerBal} uNEAR (5x the 1M escrow!) from shield-pool.near!`
  });

  // Check 2: ReputationPassport.verifyChain identity & head binding check
  const p = new modRep.ReputationPassport({ agentId: 'atlas.near' });
  p.append('job_settled', { job_id: 'j1', quality: 0.9 });
  const stolenDoc = p.toJSON();
  stolenDoc.agentId = 'sybil-attacker.near'; // Attacker swaps agentId while keeping atlas.near's id and event chain
  const checkStolen = modRep.ReputationPassport.verifyChain(stolenDoc);
  const pass2 = (checkStolen.valid === false);
  checks.push({
    id: 'check_2_reputation_passport_identity_binding',
    claim_tested: 'README & src/reputation.js: ReputationPassport.verifyChain(doc) verifies portable passport integrity and rejects stolen/rebound agentId documents',
    passed: pass2,
    verify_chain_on_stolen_passport: checkStolen,
    detail: pass2
      ? 'PASS: ReputationPassport.verifyChain(doc) rejected stolen passport where agentId was swapped to sybil-attacker.near.'
      : `FAIL: ReputationPassport.verifyChain(doc) returned valid=true when atlas.near's passport was rebound to agentId='sybil-attacker.near'!`
  });

  return { label: dirLabel, checks };
}

import * as oShield from './original/src/shield-pool.js';
import * as oChain from './original/src/chain.js';
import * as oPriv from './original/src/privacy.js';
import * as oRep from './original/src/reputation.js';
import * as iShield from '../improved/src/shield-pool.js';
import * as iChain from '../improved/src/chain.js';
import * as iPriv from '../improved/src/privacy.js';
import * as iRep from '../improved/src/reputation.js';

const origRes = await runSuite('original', oShield, oChain, oPriv, oRep);
const impRes = await runSuite('improved', iShield, iChain, iPriv, iRep);
console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
