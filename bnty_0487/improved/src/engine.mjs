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
    this.state = {
      settledNonces: new Set(),
      committedJobs: new Map(),
      lockedAmounts: new Map(),
      settledJobs: new Set(),
      claimedMilestones: new Set(),
    };
  }

  applyStep(stepName, payload) {
    if (!stepName || typeof stepName !== 'string') {
      throw new Error('stepName must be a non-empty string');
    }
    validateStepInvariants(stepName, payload, this.state);
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


export function closeEpoch({ operatingCashUsdc, reserveFloorUsdc = 1000 }) {
  if (!Number.isFinite(operatingCashUsdc) || operatingCashUsdc < reserveFloorUsdc) {
    throw new Error('operating cash below reserve floor');
  }
  const distributable = Number((operatingCashUsdc - reserveFloorUsdc).toFixed(2));
  const ownerVault = Number((distributable * 0.70).toFixed(2));
  const growthPool = Number((distributable * 0.20).toFixed(2));
  const gasBuffer = Number((distributable - ownerVault - growthPool).toFixed(2));
  return {
    reserve_floor_usdc: reserveFloorUsdc,
    distributable_profit_usdc: distributable,
    owner_vault_usdc: ownerVault,
    growth_pool_usdc: growthPool,
    gas_buffer_usdc: gasBuffer
  };
}

export function validateStepInvariants(stepName, payload, state) {
  const m = payload?.metrics || {};
  if (stepName === 'sale') {
    if (m.inventory_before - m.qty !== m.inventory_after || m.inventory_after < 0) {
      throw new Error('sale inventory conservation violated');
    }
    state.inventory = m.inventory_after;
    state.grossRevenue = m.gross_usdc;
  } else if (stepName === 'procurement') {
    if (m.cogs_ratio_bps > m.max_cogs_bps) {
      throw new Error(`COGS policy breached: ${m.cogs_ratio_bps} bps > max ${m.max_cogs_bps} bps`);
    }
    if (m.procured_units * m.unit_cost_usdc !== m.total_cogs_usdc) {
      throw new Error('procurement total_cogs_usdc arithmetic mismatch');
    }
    state.operatingCash = m.operating_cash_usdc;
  } else if (stepName === 'treasury_split') {
    const sumSplits = m.owner_vault_usdc + m.growth_pool_usdc + m.gas_buffer_usdc;
    if (Math.abs(sumSplits - m.distributable_profit_usdc) > 1e-2) {
      throw new Error('treasury_split sum does not equal distributable_profit_usdc');
    }
    if (Math.abs(m.owner_vault_usdc - m.distributable_profit_usdc * 0.70) > 1e-2 ||
        Math.abs(m.growth_pool_usdc - m.distributable_profit_usdc * 0.20) > 1e-2 ||
        Math.abs(m.gas_buffer_usdc - m.distributable_profit_usdc * 0.10) > 1e-2) {
      throw new Error('treasury_split violates 70/20/10 policy ratio');
    }
    if (state.operatingCash !== undefined && (state.operatingCash - m.distributable_profit_usdc) < m.reserve_floor_usdc) {
      throw new Error('treasury_split violates reserve_floor_usdc');
    }
  }
}
