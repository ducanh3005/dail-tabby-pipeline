import test from 'node:test';
import assert from 'node:assert/strict';
import { DeterministicStateMachine, STEPS_SPEC, sha256Hex } from '../src/engine.mjs';

test('deterministic state machine executes all 3 try-it steps identically across runs', () => {
  const m1 = new DeterministicStateMachine().runAllTryItSteps();
  const m2 = new DeterministicStateMachine().runAllTryItSteps();
  assert.equal(m1.eventCount, 3);
  assert.equal(m1.chainVerified, true);
  assert.equal(m1.headHash, m2.headHash);
  assert.deepEqual(m1.events, m2.events);
});

test('tampering with any event payload invalidates hash chain verification', () => {
  const m = new DeterministicStateMachine();
  m.runAllTryItSteps();
  assert.equal(m.verifyChain(), true);
  m.events[1].payload = { summary: 'tampered', metrics: {} };
  assert.equal(m.verifyChain(), false);
});

test('rejects empty step names', () => {
  const m = new DeterministicStateMachine();
  assert.throws(() => m.applyStep('', {}), /stepName must be a non-empty string/);
});

test('each try-it step produces non-empty metrics and valid 64-hex SHA-256 digest', () => {
  const snap = new DeterministicStateMachine().runAllTryItSteps();
  for (let i = 0; i < STEPS_SPEC.length; i++) {
    assert.equal(snap.events[i].step, STEPS_SPEC[i].step);
    assert.match(snap.events[i].hash, /^[0-9a-f]{64}$/);
    assert.ok(Object.keys(snap.events[i].payload.metrics).length > 0);
  }
});
