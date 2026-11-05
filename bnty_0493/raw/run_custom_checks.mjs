
async function runSuite(modPath, label) {
  const mod = await import(modPath);
  const { DeterministicStateMachine } = mod;
  const checks = [];

  // Check 1: Does engine enforce 90/10 inflow split and 70/30 royalty pool conservation?
  let check1Pass = false;
  let check1Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    sm.applyStep('nft_receives_funds', {
      summary: 'inflow',
      metrics: { token_id: '42', subaccount: 'vault-42.nft.near', gross_inflow_usdc: 2000, nft_treasury_usdc: 1800, royalty_pool_usdc: 200 }
    });
    let overpayBlocked = false;
    try {
      sm.applyStep('pays_royalty', {
        summary: 'overpay royalty',
        metrics: { token_id: '42', payouts: { 'creator-ava.near': 300, 'co-author-ben.near': 200 }, remaining_royalty_pool_usdc: 0 }
      });
    } catch (e) {
      overpayBlocked = true;
    }
    let distFnWorks = false;
    if (typeof mod.distributeRoyalties === 'function') {
      const r = mod.distributeRoyalties(200);
      distFnWorks = (r.payouts['creator-ava.near'] === 140 && r.payouts['co-author-ben.near'] === 60 && r.remaining_royalty_pool_usdc === 0);
    }
    check1Pass = overpayBlocked && distFnWorks;
    check1Detail = check1Pass
      ? "PASS: Overpaying royalties (500 USDC from 200 USDC pool) rejected, and distributeRoyalties(200) computes 140/60 USDC exactly."
      : `FAIL: overpayBlocked=${overpayBlocked}, distFnWorks=${distFnWorks}. Unpatched engine has no distributeRoyalties() and accepts 500 USDC payouts from a 200 USDC pool!`;
  } catch (e) {
    check1Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_1_nft_inflow_and_royalty_split_conservation",
    claim_tested: "README Step 1 & 2: 2,000 USDC inflow splits 1,800 treasury / 200 royalty pool, and distributeRoyalties(#42) pays 140 (70%) + 60 (30%)",
    passed: check1Pass,
    detail: check1Detail
  });

  // Check 2: Does verifyCredential() reject stale owners after NFT transfer?
  let check2Pass = false;
  let check2Detail = "";
  try {
    const sm = new DeterministicStateMachine();
    let staleAcceptedBlocked = false;
    try {
      sm.applyStep('presents_credential', {
        summary: 'stale owner accepted',
        metrics: { token_id: '42', credential_scope: 'tier:pro-validator', current_owner_verified: true, transferred_to: 'buyer-cara.near', stale_owner_verified: true, stale_reason: 'none' }
      });
    } catch (e) {
      staleAcceptedBlocked = true;
    }
    let credFnWorks = false;
    if (typeof mod.verifyCredential === 'function') {
      const okRes = mod.verifyCredential({ currentOwner: 'buyer-cara.near', presenter: 'buyer-cara.near', scope: 'tier:pro-validator' });
      const staleRes = mod.verifyCredential({ currentOwner: 'buyer-cara.near', presenter: 'old-owner.near', scope: 'tier:pro-validator' });
      credFnWorks = (okRes.ok === true && staleRes.ok === false && staleRes.reason === 'signer_not_current_owner');
    }
    check2Pass = staleAcceptedBlocked && credFnWorks;
    check2Detail = check2Pass
      ? "PASS: Stale owner credential presentation rejected (signer_not_current_owner) in both verifyCredential() and applyStep()."
      : `FAIL: staleAcceptedBlocked=${staleAcceptedBlocked}, credFnWorks=${credFnWorks}. Unpatched engine has no verifyCredential() and accepts stale_owner_verified=true!`;
  } catch (e) {
    check2Detail = "Error: " + e.message;
  }
  checks.push({
    id: "check_2_nft_owner_transfer_credential_revocation",
    claim_tested: "README Step 3: verifyCredential() returns ok=true for current owner and ok=false (signer_not_current_owner) for old owner after transfer",
    passed: check2Pass,
    detail: check2Detail
  });

  return { label, checks };
}

import { pathToFileURL } from 'node:url';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const origUrl = pathToFileURL(path.join(__dirname, 'original', 'src', 'engine.mjs')).href;
const impUrl = pathToFileURL(path.join(__dirname, '..', 'improved', 'src', 'engine.mjs')).href;

const origRes = await runSuite(origUrl, 'original_engine_mjs');
const impRes = await runSuite(impUrl, 'improved_engine_mjs');
console.log(JSON.stringify({ original: origRes, improved: impRes }, null, 2));
