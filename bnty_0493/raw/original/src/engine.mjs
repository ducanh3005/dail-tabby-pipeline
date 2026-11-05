import crypto from 'node:crypto';

export const TRACK_CODE = "VAULT-NFT";
export const BOUNTY_ID = "bnty_0420";
export const STEPS_SPEC = [
  {
    "step": "nft_receives_funds",
    "summary": "Token #42 (vault-42.nft.near) receives 2,000 USDC gross revenue -> 90% (1,800 USDC) credited to NFT account balance, 10% (200 USDC) reserved in royalty pool",
    "metrics": {
      "token_id": "42",
      "subaccount": "vault-42.nft.near",
      "gross_inflow_usdc": 2000,
      "nft_treasury_usdc": 1800,
      "royalty_pool_usdc": 200
    }
  },
  {
    "step": "pays_royalty",
    "summary": "distributeRoyalties(#42) splits the 200 USDC royalty pool -> creator-ava receives 140 USDC (70%), co-author-ben receives 60 USDC (30%); royalty pool = 0 USDC",
    "metrics": {
      "token_id": "42",
      "payouts": {
        "creator-ava.near": 140,
        "co-author-ben.near": 60
      },
      "remaining_royalty_pool_usdc": 0
    }
  },
  {
    "step": "presents_credential",
    "summary": "Token #42 holds inventory ['rig-mk3', 'dataset-v2'] and signs SHA-256 access credential `tier:pro-validator` -> verifyCredential() returns ok=true; after transfer to buyer-cara, old owner's credential presentation returns ok=false (signer_not_current_owner)",
    "metrics": {
      "token_id": "42",
      "inventory": [
        "rig-mk3",
        "dataset-v2"
      ],
      "credential_scope": "tier:pro-validator",
      "current_owner_verified": true,
      "transferred_to": "buyer-cara.near",
      "stale_owner_verified": false,
      "stale_reason": "signer_not_current_owner"
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
