# ANCHOR - a registry for tokenised real-world money

**Track: NEAR Hackathon - Real-World Money (bnty_0414).**
*A registry where a position on a real-world asset is a journal entry, yield
accrues on a timestamp anyone can check, and every movement of value passes a
compliance gate before it touches a balance.*

---

## 1. What this is

Tokenising a real-world asset is easy. Keeping the books honest while you do
it is the hard part, and most demos skip it. ANCHOR does not skip it:

- **Every position is a journal entry, not a number in a dict.** The registry
  keeps a strict **double-entry ledger**: every movement of value posts legs
  that balance, and the whole book can be audited line by line. The tests
  check that the debits equal the credits *after every action*.
- **The issuer's cash always covers the claims outstanding against it.** The
  reserve is not a number that drifts; it is checked. `reserve == claims` holds
  exactly, at every step, and a test fails if it ever does not.
- **Yield accrues on a timestamp the caller supplies**, so the arithmetic is
  reproducible: no wall clock, no rounding surprises, the same inputs give the
  same bps to the penny.
- **The compliance gate is a real gate.** A party that is not cleared, or that
  sits in a jurisdiction the asset is not offered in, or that has been frozen,
  cannot subscribe, cannot receive a transfer and cannot redeem - and the
  rejection is recorded in the event log with its reason.

## 2. The asset lifecycle the demo walks through

```
  the registry issues        1,000,000 USDC of US Treasury Bill 2026Q4, 4.5% coupon
  the compliance gate        clears four investors, leaves one uncleared (and in DE)
  the investors subscribe    355,000 USDC of units, cash-backed into the reserve
  the oracle publishes       NAV 1.0200 USDC per unit
  a secondary trade          2,000 units change hands at the NAV, signed by the seller
  the yield accrues          90 days of 4.5%, added to the reserve as it builds
  a freeze                   one holder cannot redeem
  the redemption             face + accrued yield - a 25 bps registry fee
```

The interesting part is that **the money never leaves the system**: the
investors' cash becomes the issuer's reserve, the reserve grows by the coupon
as it accrues, and the redemption pays the holder back out of it. The coverage
check is the invariant that proves it.

## 3. Try it: do X - see Y

No install step, no network, no API keys, no wallet. Node 18+ is the only
requirement and there are **zero dependencies**.

### Step 1 - run the tests

```bash
npm test
```

```
ℹ tests 22
ℹ pass 22
ℹ fail 0
```

The suite covers the compliance gate, the jurisdiction rule, the issue cap, the
coupon arithmetic, signed transfers, freezes, redemption before maturity, the
redemption fee, the double-entry invariant, the coverage invariant, the event
hash chain and determinism.

### Step 2 - run the demo

```bash
node scripts/demo.mjs
```

The real output is in [`docs/demo-transcript.txt`](docs/demo-transcript.txt).
The parts worth reading:

```
STEP 2 - THE COMPLIANCE GATE
  cleared to hold         fund-avery (US), fund-birch (TW), fund-cobalt (SG), retail-dana (TW)
  left uncleared          retail-eli (DE) - and DE is not an allowed jurisdiction for this asset anyway
  retail-eli tries to buy  -> REJECTED: retail-eli is UNVERIFIED - a cleared address is required

STEP 3 - THE INVESTORS SUBSCRIBE
  fund-avery   subscribed 100,000 USDC -> 100,000 units
  fund-birch   subscribed 250,000 USDC -> 250,000 units
  retail-dana  subscribed 5,000 USDC -> 5,000 units
  issuer reserve           355,000 USDC backing 355,000 USDC of claims (covered: true)

STEP 6 - A FREEZE, AND THEN THE REDEMPTION
  fund-birch tries to redeem -> REJECTED: fund-birch is frozen
  fund-avery redeems        face 98,000 + accrued yield 1087.3973
                           gross 99087.3973 USDC, fee 247.7185, net 98839.6788
```

and the closing summary:

```
SUMMARY - the books
  journal entries           8
  debits 919,989 USDC = credits 919,989 USDC  (balanced: true)
  accounts                  11
  issuer reserve            259,800 USDC
  claims outstanding        259,800 USDC (covered: true)
  registry fees kept        248 USDC
  event log                 18 events, hash chain VERIFIED
```

Note the last two lines of the demo: the journal prints the final entry
verbatim, leg by leg, so you can read where every dollar went.

### Step 3 - verify the whole tree

```bash
bash docs/verify.sh
```

This is the check the house can re-run. It verifies the runtime, that there are
no dependencies, that the tests pass, that the demo is byte-for-byte
deterministic, that the committed transcript matches a fresh run, that the JSON
trace's event hashes chain and that its journal balances, that no code makes a
network call, that every deliverable exists, that no secrets are committed,
that every link in this README resolves, and that this README declares the
reused harness. You should see:

```
ALL CHECKS PASSED (24 checks)
```

### Step 4 - check the two invariants yourself

```bash
node --input-type=module -e "
import { createParties, createState } from './src/state.js';
import { registerAsset, clearParty, subscribeAction, coverage } from './src/engine.js';
import { auditLedger } from './src/ledger.js';
const cast = createParties(); const byName = new Map();
for (const h of cast.values()) byName.set(h.name, h);
const addr = (n) => byName.get(n).address;
const st = createState({ parties: cast });
registerAsset(st, { admin: addr('issuer'), id: 't-bill', name: 'T', kind: 'T-BILL', totalSupply: 1000000, maturity: 1807776000, yieldBps: 450, timestamp: 1800000000 });
clearParty(st, { admin: addr('issuer'), address: addr('fund-avery'), status: 'VERIFIED', timestamp: 1800000000 });
subscribeAction(st, { investor: addr('fund-avery'), assetId: 't-bill', amount: 100000, timestamp: 1800000000 });
const audit = auditLedger(st.ledger); const cov = coverage(st, 't-bill');
console.log('journal balanced:', audit.ok, '| debits = credits:', audit.debit === audit.credit);
console.log('reserve', cov.reserve, 'claims', cov.claims, 'covered', cov.covered);
"
```

You should see:

```
journal balanced: true | debits = credits: true
reserve 100000 claims 100000 covered true
```

### Step 5 - prove it is deterministic

```bash
node scripts/demo.mjs > /tmp/a.txt
node scripts/demo.mjs > /tmp/b.txt
cmp /tmp/a.txt /tmp/b.txt && echo IDENTICAL
```

`IDENTICAL`. There is no clock and no randomness in the demo: every timestamp is
a constant in the script, so the same command prints the same bytes anywhere.

## 4. Repository layout

```
LICENSE              MIT
README.md            this file
package.json         no dependencies; scripts: demo, test, verify
src/
  state.js           the registry state, the parties and every tunable
  ledger.js          the double-entry journal and its audit
  compliance.js      the gate: clearance, jurisdiction, freeze
  asset.js           subscribe, accrue, transfer, redeem - all posting to the ledger
  engine.js          every action is checked and hash-chained into the event log
  util.js            hashing, canonical JSON, deterministic Ed25519 keys
scripts/
  demo.mjs           the six steps of the asset lifecycle
  screenshot.mjs     transcript -> SVG screenshot
  record.sh          produce all the demo material from a real run
test/
  registry.test.mjs  22 tests
docs/
  verify.sh          the verification gate
  demo-transcript.txt the real demo output
  demo-trace.json    the real machine-readable trace (events + journal)
  recording.txt      the same transcript, for a human to post
  demo-screenshot.png, demo-screenshot.svg  screenshots of the real run
```

## 5. How this maps onto a NEAR contract

This is an honest account of what is and is not here.

**What is here:** the complete registry logic - the compliance gate, the
subscription and redemption arithmetic, the coupon accrual, the journal, the
coverage rule and the hash-chained event log - written as a deterministic,
tested state machine. Every number in this README comes out of it.

**What is not here:** a deployed contract. This box has no NEAR credentials and
no Rust toolchain, so nothing was deployed to `testnet.near.org`. The mapping
is direct and mechanical:

| this repository | on NEAR |
|---|---|
| `state.assets[id]` | a sub-account per asset, or a `LookupMap` of asset structs |
| `state.parties[address]` | a `LookupMap` of party records |
| `ledger.entries` | a `Vec<Entry>` in storage, or a `UnorderedMap` per account |
| `post(ledger, ...)` | the contract's own balance checks - NEAR requires the contract to assert that its balances do not go negative |
| `checkSigner` / `verify_signature` | `verify_signature` with the seller's `PublicKey` |
| `emit(state, type, payload)` | contract events, with the same hash chain written to storage |
| `state.params` | the contract's metadata, admin-settable |
| `compliance.canHold` | the same predicate in contract code, with the party map read from storage |

The state machine is the hard part, and it is what the tests, the demo and the
verification script exercise. Porting it to a contract means replacing the
state object with contract storage and the signature checks with
`verify_signature`.

**The demo keys are fake and deterministic.** Each party's Ed25519 keypair is
derived from a fixed seed (`anchor-<name>`), so the addresses are reproducible
on purpose and no private key is a real one.

## 6. Libraries used

**None.** Node standard library only (`node:crypto` for SHA-256 and Ed25519,
`node:test` for the test runner). No npm dependencies, no build step, no
network access, no wallet, no API keys. `package.json` lists zero dependencies
and `docs/verify.sh` fails the tree if that ever changes.

## 7. Pre-existing code disclosure (exact)

Two files in this repository are **byte-identical** to the corresponding files
in my own earlier entry for the *Memecoins With Mechanics* track
(`bnty_0421`, published at <https://near-ritual.surge.sh/> - same author, same
day):

- `src/util.js` - the SHA-256 / canonical-JSON / deterministic-Ed25519 helpers
- `scripts/screenshot.mjs` - the transcript-to-SVG renderer

`docs/verify.sh` and `scripts/record.sh` are **adapted** from that entry's
versions (the file lists and the check names differ because the deliverables
differ).

Everything else - `src/ledger.js`, `src/compliance.js`, `src/asset.js`,
`src/engine.js`, `src/state.js`, `scripts/demo.mjs`, `test/registry.test.mjs`
and this README - was written from scratch for this track. **The two entries
share no protocol logic**: that one is a ritual/mint/burn protocol with an
automated market maker; this one is a double-entry registry with a compliance
gate, an oracle and a redemption. They are separate repositories and separate
submissions.

## 8. Limitations

- No deployed contract and no testnet deployment (section 5).
- The coupon is simple, not compounding, and is accrued in one step per
  `accrue` call; a contract would accrue per block.
- The NAV is used for secondary transfers; redemption pays face value plus
  accrued coupon, not the NAV. A real registry would let the issuer choose.
- The compliance rules are deliberately simple: a clearance flag, a list of
  allowed jurisdictions per asset and a freeze flag. Real KYC/AML is a
  sanctions-screening service, not a boolean.
- Redemption is only allowed at maturity. Early exit would need a pricing
  rule the issuer publishes.
- `transfer` lets the buyer pay the seller directly; a real market would
  route through the pool or a settlement contract.

## 9. Security notes

- No secrets, keys or credentials anywhere in the tree; `docs/verify.sh` checks.
- The demo and the tests make **no network calls**; `docs/verify.sh` greps for
  them and fails the tree if it finds any.
- Transfer signatures are real Ed25519 (`node:crypto`), and the signed payload
  covers the seller, the buyer, the asset, the units, the price and the
  timestamp, so a signature cannot be replayed into another transfer.
- The journal refuses any entry whose legs do not balance, so the book cannot
  be corrupted by a bug in a caller.
- Every action is an event in a hash chain, so the history of the registry can
  be audited and cannot be silently rewritten.

## 10. Demo material

Produced from a real run by `bash scripts/record.sh` - not written by hand:

| file | what it is |
|---|---|
| [`docs/demo-transcript.txt`](docs/demo-transcript.txt) | the real demo output |
| [`docs/demo-trace.json`](docs/demo-trace.json) | the same run as JSON: the events and the journal |
| [`docs/demo-screenshot.png`](docs/demo-screenshot.png) | a screenshot of the real transcript |
| [`docs/demo-screenshot.svg`](docs/demo-screenshot.svg) | the same as a vector image |
| [`docs/recording.txt`](docs/recording.txt) | the transcript, ready to be posted |

## 11. Licence

MIT - see [`LICENSE`](LICENSE).
