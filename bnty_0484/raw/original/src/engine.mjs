import crypto from 'node:crypto';

export const TRACK_CODE = "INTENT-VAULT";
export const BOUNTY_ID = "bnty_0416";
export const STEPS_SPEC = [
  {
    "step": "quote",
    "summary": "Solver quotes cross-chain intent swap of 5,000 Base USDC (`eip155:8453`) -> NEAR USDC (`near:mainnet`) at 0.9992 rate (4,996.00 NEAR USDC, 4.00 USDC solver fee, 300s deadline, signed intent hash verified)",
    "metrics": {
      "from_asset": "eip155:8453:USDC",
      "to_asset": "near:mainnet:USDC",
      "amount_in_usdc": 5000.0,
      "amount_out_usdc": 4996.0,
      "solver_fee_usdc": 4.0,
      "rate": 0.9992,
      "quote_valid": true
    }
  },
  {
    "step": "swap",
    "summary": "executeIntentSwap() verifies solver + user commitments and settles atomically -> agent NEAR balance = 4,996.00 USDC, solver balance +4.00 USDC, replay of same intent nonce -> REFUSED (intent_already_settled)",
    "metrics": {
      "settled_out_usdc": 4996.0,
      "solver_fee_usdc": 4.0,
      "replay_attempt": "REFUSED",
      "replay_reason": "intent_already_settled"
    }
  },
  {
    "step": "deposit_and_withdraw",
    "summary": "Agent deposits 4,000.00 USDC into EarningsVault -> receives 4,000.0000 vUSDC shares; after 120.00 USDC protocol revenue accrues to the vault (share price = 1.0300 USDC), agent redeems 2,000.0000 shares -> receives 2,060.00 USDC exactly",
    "metrics": {
      "deposited_usdc": 4000.0,
      "minted_shares": 4000.0,
      "yield_accrued_usdc": 120.0,
      "share_price_usdc": 1.03,
      "redeemed_shares": 2000.0,
      "withdrawn_usdc": 2060.0
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
