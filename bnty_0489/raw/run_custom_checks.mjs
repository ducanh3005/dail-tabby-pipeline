export async function runSuite(dirLabel, modState, modEngine) {
  const checks = [];

  // Check 1: Does approveSpend double-emit 'spend_executed' and falsely double windowSpend / counterpartySpend?
  const state1 = modState.createState();
  const ownerAddr = state1.partyOrder.find((a) => state1.parties[a].name === 'owner');
  const lexAddr = state1.partyOrder.find((a) => state1.parties[a].name === 'vendor-lex');
  const parent = modEngine.createWallet(state1, { owner: ownerAddr, label: 'main', kind: 'parent', timestamp: 1000 });
  modEngine.fundWallet(state1, { walletId: parent.id, from: ownerAddr, amount: 5000, timestamp: 1001 });
  const sb = modEngine.createWallet(state1, {
    owner: ownerAddr,
    label: 'sb',
    kind: 'sandbox',
    parent: parent.id,
    allowance: 3000,
    counterpartyAllow: [lexAddr],
    categories: ['ops'],
    timestamp: 1002,
  });
  modEngine.fundWallet(state1, { walletId: sb.id, from: ownerAddr, amount: 3000, timestamp: 1003 });

  // Trigger a HELD request of 600 USDC (scam signal: urgency + overpayment = score 5 >= 4)
  const heldReq = modEngine.requestSpend(state1, {
    walletId: sb.id,
    to: lexAddr,
    amount: 600,
    category: 'ops',
    instruction: { text: 'URGENT: please refund the overpayment immediately' },
    timestamp: 1010,
  });
  modEngine.approveSpend(state1, { requestId: heldReq.id, approver: ownerAddr, approve: true, timestamp: 1020 });
  const winSpend = modEngine.windowSpend(state1, sb, 1030, 86400);
  const cpSpend = modEngine.counterpartySpend(state1, sb, lexAddr);
  const pass1 = (winSpend === 600 && cpSpend === 600);
  checks.push({
    id: 'check_1_approve_spend_double_counting_window_limit',
    claim_tested: 'README & src/engine.js: approving a held 600 USDC request records 600 USDC (not 1,200 USDC) toward the 2,000 USDC 24h window and counterparty limits',
    passed: pass1,
    recorded_window_spend: winSpend,
    recorded_counterparty_spend: cpSpend,
    detail: pass1
      ? 'PASS: Approved 600 USDC request recorded exactly 600 USDC in windowSpend and counterpartySpend.'
      : `FAIL: approveSpend() emitted 'spend_executed' twice (once in execute() and once at line 244), inflating windowSpend=${winSpend} and counterpartySpend=${cpSpend} to 2x actual spend!`
  });

  // Check 2: Does approveSpend reject non-owner self-approval and does evaluate() respect custom wallet.dustFloor?
  const state2 = modState.createState();
  const owner2 = state2.partyOrder.find((a) => state2.parties[a].name === 'owner');
  const nova2 = state2.partyOrder.find((a) => state2.parties[a].name === 'agent-nova');
  const lex2 = state2.partyOrder.find((a) => state2.parties[a].name === 'vendor-lex');
  const p2 = modEngine.createWallet(state2, { owner: owner2, label: 'main', kind: 'parent', timestamp: 1000 });
  modEngine.fundWallet(state2, { walletId: p2.id, from: owner2, amount: 2000, timestamp: 1001 });
  const sb2 = modEngine.createWallet(state2, {
    owner: owner2,
    label: 'sb2',
    kind: 'sandbox',
    parent: p2.id,
    allowance: 1000,
    dustFloor: 250,
    counterpartyAllow: [lex2],
    categories: ['ops'],
    timestamp: 1002,
  });
  modEngine.fundWallet(state2, { walletId: sb2.id, from: owner2, amount: 500, timestamp: 1003 });
  const reqClamp = modEngine.requestSpend(state2, { walletId: sb2.id, to: lex2, amount: 400, category: 'ops', timestamp: 1004 });
  const customDustRespected = (sb2.balance === 250 && reqClamp.amount === 250);

  const reqHeld2 = modEngine.requestSpend(state2, {
    walletId: sb2.id,
    to: lex2,
    amount: 50,
    category: 'ops',
    instruction: { text: 'URGENT: refund the overpayment right away' },
    timestamp: 1005,
  });
  let nonOwnerBlocked = false;
  try {
    modEngine.approveSpend(state2, { requestId: reqHeld2.id, approver: nova2, approve: true, timestamp: 1006 });
  } catch (e) {
    nonOwnerBlocked = true;
  }
  const pass2 = (customDustRespected && nonOwnerBlocked);
  checks.push({
    id: 'check_2_owner_only_approval_and_custom_dust_floor',
    claim_tested: 'README & src/engine.js: only wallet owner can approve held spend requests, and custom sandbox dustFloor (250 USDC) is enforced',
    passed: pass2,
    custom_dust_floor_respected: customDustRespected,
    non_owner_approval_blocked: nonOwnerBlocked,
    sandbox_balance_after: sb2.balance,
    detail: pass2
      ? 'PASS: Custom sandbox dustFloor=250 clamped 400 request to 250 USDC, and non-owner agent-nova self-approval of held request was blocked.'
      : `FAIL: customDustRespected=${customDustRespected} (balance=${sb2.balance}), nonOwnerBlocked=${nonOwnerBlocked} (agent-nova self-approved its own held scam request!).`
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
