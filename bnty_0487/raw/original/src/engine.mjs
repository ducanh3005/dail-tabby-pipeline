import crypto from 'node:crypto';

export const TRACK_CODE = "INTENT-SHOP";
export const BOUNTY_ID = "bnty_0417";
export const STEPS_SPEC = [
  {
    "step": "sale",
    "summary": "Customer settles cross-chain NEAR Intent (`eip155:8453:USDC -> near:USDC`, 1,000 USDC) for 10 API-Audit packs -> order fulfilled, gross revenue = 1,000 USDC, inventory 15 -> 5 units",
    "metrics": {
      "intent_chain": "eip155:8453->near:mainnet",
      "sku": "API-AUDIT-PACK",
      "qty": 10,
      "gross_usdc": 1000,
      "inventory_before": 15,
      "inventory_after": 5
    }
  },
  {
    "step": "procurement",
    "summary": "Inventory (5) <= reorder point (6) triggers autonomous procurement of 20 upstream units at 18 USDC/unit (360 USDC total, COGS ratio 36% <= human max 45%) -> inventory = 25 units, operating cash = 1,640 USDC",
    "metrics": {
      "reorder_point": 6,
      "procured_units": 20,
      "unit_cost_usdc": 18,
      "total_cogs_usdc": 360,
      "cogs_ratio_bps": 3600,
      "max_cogs_bps": 4500,
      "inventory_after": 25,
      "operating_cash_usdc": 1640
    }
  },
  {
    "step": "treasury_split",
    "summary": "closeEpoch() enforces 1,000 USDC reserve floor and splits 640 USDC distributable profit -> 70% (448 USDC) to human owner vault, 20% (128 USDC) to growth pool, 10% (64 USDC) to agent compute gas buffer",
    "metrics": {
      "reserve_floor_usdc": 1000,
      "distributable_profit_usdc": 640,
      "owner_vault_usdc": 448,
      "growth_pool_usdc": 128,
      "gas_buffer_usdc": 64
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
