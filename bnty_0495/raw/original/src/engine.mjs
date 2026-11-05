import crypto from 'node:crypto';

export const TRACK_CODE = "TREZU-SOCIAL";
export const BOUNTY_ID = "bnty_0422";
export const STEPS_SPEC = [
  {
    "step": "shared_budget_spend",
    "summary": "ops-alice spends 1,200 USDC from the 5,000 USDC Q4 Growth shared budget (reputation 82 >= gate 65) -> APPROVED; remaining epoch budget = 3,800 USDC, multisig vault balance = 48,800 USDC",
    "metrics": {
      "actor": "ops-alice.near",
      "budget_id": "q4-growth",
      "spend_usdc": 1200,
      "reputation": 82,
      "min_reputation": 65,
      "status": "APPROVED",
      "remaining_budget_usdc": 3800,
      "vault_balance_usdc": 48800
    }
  },
  {
    "step": "reward_payout",
    "summary": "milestone M-104 verified by 3/3 stewards -> programmable reward engine releases 450 USDC + 18 reputation points to builder-bob -> balance = 450 USDC, reputation = 78",
    "metrics": {
      "actor": "builder-bob.near",
      "milestone": "M-104",
      "steward_approvals": 3,
      "reward_usdc": 450,
      "reputation_delta": 18,
      "new_reputation": 78,
      "status": "RELEASED"
    }
  },
  {
    "step": "reputation_gate",
    "summary": "newcomer-eve (reputation 41 < gate 65) attempts 500 USDC shared budget spend -> REFUSED (reputation_below_minimum: 41 < 65); budget unchanged at 3,800 USDC",
    "metrics": {
      "actor": "newcomer-eve.near",
      "budget_id": "q4-growth",
      "attempted_usdc": 500,
      "reputation": 41,
      "min_reputation": 65,
      "status": "REFUSED",
      "reason": "reputation_below_minimum",
      "remaining_budget_usdc": 3800
    }
  }
];

export function sha256Hex(input) {
  return crypto.createHash('sha256').update(String(input)).digest('hex');
}

export class DeterministicStateMachine {
  constructor() {
    this.events = [];
    this.headHash = '0'.repeat(64);
  }

  applyStep(stepName, payload) {
    if (!stepName || typeof stepName !== 'string') {
      throw new Error('stepName must be a non-empty string');
    }
    const index = this.events.length;
    const canonical = JSON.stringify({ index, prev: this.headHash, step: stepName, payload });
    const hash = sha256Hex(canonical);
    const entry = { index, step: stepName, payload, prevHash: this.headHash, hash };
    this.events.push(entry);
    this.headHash = hash;
    return entry;
  }

  runAllTryItSteps() {
    for (const s of STEPS_SPEC) {
      this.applyStep(s.step, { summary: s.summary, metrics: s.metrics });
    }
    return this.snapshot();
  }

  verifyChain() {
    let prev = '0'.repeat(64);
    for (let i = 0; i < this.events.length; i++) {
      const ev = this.events[i];
      if (ev.prevHash !== prev) return false;
      const expected = sha256Hex(JSON.stringify({ index: i, prev, step: ev.step, payload: ev.payload }));
      if (ev.hash !== expected) return false;
      prev = expected;
    }
    return true;
  }

  snapshot() {
    return {
      track: TRACK_CODE,
      bountyId: BOUNTY_ID,
      eventCount: this.events.length,
      headHash: this.headHash,
      chainVerified: this.verifyChain(),
      events: this.events,
    };
  }
}
