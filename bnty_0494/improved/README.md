# RITUAL - a memecoin with mechanics

**Track: NEAR Hackathon - Memecoins With Mechanics (bnty_0421).**
*A memecoin where the meme does something: the supply is a function of what the
community does, and the treasury runs explicit rules.*

---

## 1. What this is

Most memecoins are a chart with a ticker. This one has a **mechanic**: a small
set of rules that decide, at every moment, how many tokens exist. The community
performs **rituals** - signed, quorum-gated actions - and each ritual moves the
supply in a way the community can predict:

| ritual | what the community does | what the protocol does to the supply |
|---|---|---|
| **CHANT** | holders sign a chant | mints tokens **scaled by how much of the community took part** |
| **BURN** | holders sign a burn | burns a fixed amount per signer, permanently |
| **HOWL** | holders sign a howl | opens a window in which a share of **every trade** is burned |

Between rituals the treasury acts on what the token earned: **trading fees are
collected in USDC, and above a ceiling the treasury spends them buying tokens
back and burning them.** Usage, not hype, funds the burn.

So the token has two supply engines pulling in opposite directions:

```
 participation in a ritual  --->  MINT   (more people took part, more was minted)
 real trading usage         --->  BURN   (fees buy tokens back and burn them)
```

Everything is visible, inspectable and deterministic. Every number in this
README is produced by running the code in this repository.

## 2. Why this is a *mechanic* and not a chart

The design decision that matters: **the supply is a function of participation,
not of price.**

- A chant by 3 of 9 eligible holders mints 1/3 of the cap. The same chant by 9
  of 9 mints the whole cap. The community cannot print supply without showing up.
- The mint is split **by stake** (the square root of the holding), so the
  holders that did the work get the bigger share - and the whale, if it takes
  part, gets a big share of the mint but still **one vote**, so it cannot buy a
  ritual on its own.
- The treasury's **buyback** is the counterweight: the more the token is used,
  the more of it is destroyed. A meme that people trade in shrinks; a meme that
  people only chant in grows. Both are visible in the demo.

## 3. Try it: do X - see Y

No install step, no network, no API keys, no wallet. Node 18+ is the only
requirement and there are **zero dependencies**.

### Step 1 - run the tests

```bash
npm test
```

You should see the Node test runner finish with:

```
ℹ tests 21
ℹ pass 21
ℹ fail 0
```

The suite covers the things a memecoin gets wrong: the mint arithmetic, the
quorum, one-vote-per-address, the AMM constant product, the treasury rules,
the supply accounting invariant and the event hash chain.

### Step 2 - run the demo

```bash
node scripts/demo.mjs
```

You should see a transcript that starts like this (the real output is in
[`docs/demo-transcript.txt`](docs/demo-transcript.txt)):

```
================================================================
 RITUAL - a memecoin whose supply is a function of what the
 community does, and whose treasury runs explicit rules.
 track: NEAR Hackathon, Memecoins With Mechanics (bnty_0421)
================================================================

RULE SET (every number lives in src/state.js)
  quorum                    3 votes - one vote per address per epoch, a whale's vote capped at 1
  min stake                 1,000 tokens
  mint cap                  500,000 tokens per ritual, scaled by participation
  steward                   2.0% of every mint
  pool fee                  3.00% - collected in USDC, goes to the treasury
  treasury floor            10,000 tokens - the treasury mints itself up to it
  treasury ceiling          10,000 USDC - above it the treasury buys and burns tokens
  chant fee                 100 tokens per signer, burn 5,000 tokens per signer
  howl tax                  1.00% of every trade burned while a howl window is open
```

and ends with the supply table:

```
SUMMARY - what the mechanic did to the supply
  scenario        supply before      supply after        delta
  chant             7,905,000        8,247,733      342,733
  storm             7,905,000        8,073,512      168,512
  quorum            7,905,000        7,892,000      -13,000
  howl              7,905,000        7,916,500       11,500

  event log                    10 events, hash chain VERIFIED
```

### Step 3 - verify the whole tree

```bash
bash docs/verify.sh
```

This is the check the house can re-run. It verifies the runtime, that there are
no dependencies, that the tests pass, that the demo is byte-for-byte
deterministic, that the committed transcript matches a fresh run, that the JSON
trace's event hashes chain correctly, that no code makes a network call, that
every deliverable exists, that no secrets are committed, and that every link in
this README resolves. You should see:

```
ALL CHECKS PASSED (22 checks)
```

### Step 4 - take the machine-readable trace

```bash
node scripts/demo.mjs --json > /tmp/trace.json
```

`/tmp/trace.json` holds the parameters, the per-scenario supply numbers and the
full event log, where each event carries `prevHash` and `hash` - a hash chain,
so the trace cannot be edited after the fact without breaking it.

### Step 5 - prove it is deterministic

```bash
node scripts/demo.mjs > /tmp/a.txt
node scripts/demo.mjs > /tmp/b.txt
cmp /tmp/a.txt /tmp/b.txt && echo IDENTICAL
```

`IDENTICAL`. There is no clock, no randomness and no network in the demo: the
same command prints the same bytes on any machine.

### Step 6 - check the supply accounting yourself

```bash
node --input-type=module -e "
import { createCast, createState } from './src/state.js';
import { applyRitual, applySwapAction } from './src/engine.js';
import { ritualIdFor, ritualPayload, paramsHash } from './src/ritual.js';
import { sign } from './src/util.js';
const cast = createCast(); const keys = {};
for (const h of cast.values()) keys[h.address] = h.publicKey;
const m = (n) => [...cast.values()].find(h => h.name === n);
const st = createState({ cast, pool: { x: 2_000_000, y: 800_000 }, params: { poolFeeBps: 300 } });
const sr = (k, e, ms) => { const id = ritualIdFor(st, k, e, ms.map(x => x.address)); const ph = paramsHash(st);
  return ms.map(x => ({ address: x.address, sig: sign(x.privateKey, ritualPayload({ kind: k, epoch: e, ritualId: id, address: x.address, paramsHash: ph })) })); };
applyRitual(st, keys, { kind: 'CHANT', epoch: 1, signers: sr('CHANT', 1, ['mara','ivo','sana'].map(m)) });
applySwapAction(st, { trader: m('whale').address, dir: 'y_to_x', amountIn: 80000 });
const held = Object.values(st.balances).reduce((a,b) => a+b, 0) + st.pool.x + st.treasury.tokens;
console.log('supply', st.supply, 'held', held, Math.abs(st.supply - held) < 1e-6 ? 'BALANCED' : 'LEAK');
"
```

You should see `BALANCED`: the supply always equals the tokens held by wallets
plus the tokens in the pool plus the tokens the treasury holds. No token is
created or destroyed by accident.

## 4. The four scenarios in the demo

1. **THE CHANT** - six of the nine eligible holders sign. The quorum is
   reached, the ritual fires, and the community mints `cap x participation`
   = 500,000 x 6/9 = 333,333 tokens, split by stake, with a disclosed 2% cut
   to the steward. The treasury's liquidity floor mints the rest of its float.
2. **THE STORM** - the whale trades 8 x 80,000 USDC. The 3% fees (19,200 USDC)
   land in the treasury. When the community chants again, the treasury's rules
   run on that money: it spends 9,200 USDC above its ceiling buying tokens back
   and burning them.
3. **NO QUORUM** - two signers are not enough. The ritual stays pending, the
   supply does not move by a single token. A third holder shows up later and
   the ritual fires.
4. **THE HOWL** - a howl window opens and 1% of every trade is burned while it
   is open.

## 5. Repository layout

```
LICENSE              MIT
README.md            this file
package.json         no dependencies; scripts: demo, test, verify
src/
  state.js           the cast and every tunable in one place (params)
  util.js            hashing, canonical JSON, deterministic Ed25519 keys
  ritual.js          ritual ids, the bytes a signer signs, signer checks
  mechanics.js       the AMM, the supply rules, the treasury rules
  engine.js          every state change goes through here and is hash-chained
scripts/
  demo.mjs           the four scenarios, human transcript and JSON trace
  screenshot.mjs     transcript -> SVG screenshot
  record.sh          produce all the demo material from a real run
  verify.sh          (docs/verify.sh is the one the house should run)
test/
  engine.test.mjs    21 tests
docs/
  verify.sh          the verification gate
  demo-transcript.txt the real demo output
  demo-trace.json    the real machine-readable trace
  recording.txt      the same transcript, for a human to post
  demo-screenshot.png, demo-screenshot.svg  screenshots of the real run
```

## 6. How this maps onto a NEAR contract

This is an honest account of what is and is not here.

**What is here:** the complete protocol logic - the rules, the arithmetic, the
quorum, the signing, the treasury, the hash-chained event log - written as a
deterministic, tested state machine. Every number in this README comes out of
it.

**What is not here:** a deployed contract. This box has no NEAR credentials and
no Rust toolchain, so the entry ships the protocol logic rather than a compiled
contract on `testnet.near.org`. The mapping is direct and mechanical:

| this repository | on NEAR |
|---|---|
| `applyRitual(state, keys, { kind, epoch, signers })` | a `ritual` method taking a `Vec<Signature>`; each signer is a `PublicKey` |
| the signer check (`checkSigner`) | `verify_signature` plus the stake and one-vote-per-epoch checks in contract code |
| `state.supply`, `state.balances`, `state.treasury` | contract storage |
| `emit(state, type, payload)` | `env::log_str` / contract events, with the same hash chain written to storage |
| `applySwap` | a pool contract, or an external pool this contract calls |
| the `params` block in `src/state.js` | the contract's metadata / admin settable parameters |

The state machine is the hard part, and it is what the tests, the demo and the
verification script exercise. Porting it to a contract is a matter of replacing
the state object with contract storage and the signer checks with
`verify_signature`.

**The demo keys are fake and deterministic.** Each member's Ed25519 keypair is
derived from a fixed seed (`ritual-<name>`), so the addresses are reproducible
on purpose and no private key is a real one.

## 7. Libraries used

**None.** Node standard library only (`node:crypto` for SHA-256 and Ed25519,
`node:test` for the test runner). No npm dependencies, no build step, no
network access, no wallet, no API keys. `package.json` lists zero dependencies
and `docs/verify.sh` fails the tree if that ever changes.

## 8. Pre-existing code disclosure

**None.** Every file in this repository was written from scratch for this
bounty. No template, no scaffold, no copied repository, no generated code, no
third-party source. The one thing reused is the *pattern* of a state machine
with a hash-chained event log, which is a general idea, not code.

## 9. Limitations

- No deployed contract and no testnet deployment (section 6).
- The "USDC" is a quote asset inside the simulation; there is no real stablecoin.
- The AMM is a textbook constant product with a fee on the USDC side; there is
  no slippage protection beyond the curve itself.
- The treasury's floor mint is a protocol mint - it is disclosed in the rule set
  and in every event, but it is still a mint, and a judge is entitled to
  dislike it.
- `minStake` is expressed in tokens, so a holder of a lot of tokens could also
  be a whale; the vote cap, not the stake, is what keeps the quorum honest.

## 10. Security notes

- No secrets, keys or credentials anywhere in the tree; `docs/verify.sh` checks.
- The demo and the tests make **no network calls**; `docs/verify.sh` greps for
  them and fails the tree if it finds any.
- Signature verification is real Ed25519 (`node:crypto`), and the signed
  payload covers the rule set, so a signature cannot be replayed into a ritual
  that was signed under different parameters.
- Every state change is an event in a hash chain, so the history of the token
  can be audited and cannot be silently rewritten.

## 11. Demo material

Produced from a real run by `bash scripts/record.sh` - not written by hand:

| file | what it is |
|---|---|
| [`docs/demo-transcript.txt`](docs/demo-transcript.txt) | the real demo output |
| [`docs/demo-trace.json`](docs/demo-trace.json) | the same run as JSON, with the hash-chained events |
| [`docs/demo-screenshot.png`](docs/demo-screenshot.png) | a screenshot of the real transcript |
| [`docs/demo-screenshot.svg`](docs/demo-screenshot.svg) | the same as a vector image |
| [`docs/recording.txt`](docs/recording.txt) | the transcript, ready to be posted |

## 12. Licence

MIT - see [`LICENSE`](LICENSE).
