import test from 'node:test'
import assert from 'node:assert/strict'
import { inspectRegressionSummary, parseRegressionPolicy } from '../dist/index.js'

const policy = {schema_version:'ketqat.regression.policy.v1', changed_axes:['circuit'],
  resources:{two_qubit_gates:{absolute_increase:0,relative_increase:.1}}, max_total_variation:null, family_alpha:.01}
const record = () => ({schema_version:'ketqat.regression.summary.v1', provenance:'CLIENT_REPORTED',
  case_key:'a'.repeat(64), baseline_sha256:'b'.repeat(64),candidate_sha256:'c'.repeat(64),
  baseline_status:'EXECUTED',candidate_status:'EXECUTED',policy:structuredClone(policy),changed_fields:['circuit_sha256'],
  resources:{baseline:{two_qubit_gates:10},candidate:{two_qubit_gates:12}},distribution:null,verdict:'REGRESSION',exit_code:1})

test('server recalculates resource threshold and rejects forged success/exit', () => {
  assert.equal(inspectRegressionSummary(record()).checks[0].maximum, 11)
  assert.throws(() => inspectRegressionSummary({...record(),verdict:'WITHIN_POLICY',exit_code:0}), /contradicts/)
  assert.throws(() => inspectRegressionSummary({...record(),exit_code:0}), /contradicts/)
  const within=record(); within.resources.candidate.two_qubit_gates=11; within.verdict='WITHIN_POLICY'; within.exit_code=0
  assert.equal(inspectRegressionSummary(within).summary.verdict,'WITHIN_POLICY')
})

test('rejects unselected, unknown and non-finite data at every boundary', () => {
  for(const extra of [{source:'secret'}, {repository:'private'}, {raw_counts:{'00':2}}]) assert.throws(()=>inspectRegressionSummary({...record(),...extra}))
  const bad=record(); bad.resources.candidate.depth=3
  assert.throws(()=>inspectRegressionSummary(bad),/redacted/)
  for(const value of [Infinity, NaN, -1, true]) {
    const invalid=record(); invalid.resources.candidate.two_qubit_gates=value
    assert.throws(()=>inspectRegressionSummary(invalid))
  }
  assert.throws(()=>parseRegressionPolicy({...policy,resources:{},max_total_variation:null}))
  assert.throws(()=>parseRegressionPolicy({...policy,changed_axes:['circuit','circuit']}))
  assert.throws(()=>parseRegressionPolicy({...policy,resources:{depth:{absolute_increase:0,relative_increase:10}}}))
})

test('no data and small shot budgets remain inconclusive; fixed drift is incompatible', () => {
  const missing=record(); missing.resources.candidate=null;missing.verdict='INCONCLUSIVE';missing.exit_code=2
  assert.equal(inspectRegressionSummary(missing).summary.verdict,'INCONCLUSIVE')
  const sampled=record();sampled.policy.resources={};sampled.policy.max_total_variation=.05
  sampled.resources={baseline:null,candidate:null}; sampled.distribution={estimate:0,method:'HOEFFDING_ALL_OUTCOMES',qubits:2,baseline_shots:20,candidate_shots:20}
  sampled.verdict='INCONCLUSIVE';sampled.exit_code=2
  assert.equal(inspectRegressionSummary(sampled).checks[0].upper,1)
  const drift=record();drift.changed_fields=['environment.python'];drift.resources={baseline:null,candidate:null};drift.verdict='INCOMPATIBLE';drift.exit_code=3
  assert.equal(inspectRegressionSummary(drift).summary.verdict,'INCOMPATIBLE')
  assert.throws(()=>inspectRegressionSummary({...drift,resources:record().resources}),/stopped/)
})


test('explicit undefined optional fields are rejected before arithmetic', () => {
  for (const metric of ['depth', 'size', 'two_qubit_gates']) {
    assert.throws(() => parseRegressionPolicy({...policy, resources:{[metric]:undefined}}), /Omit unselected fields/)
    const invalid=record(); invalid.policy.resources[metric]=undefined
    assert.throws(() => inspectRegressionSummary(invalid), /Omit unselected fields/)
    const observation=record(); observation.resources.candidate[metric]=undefined
    assert.throws(() => inspectRegressionSummary(observation), /Omit unselected fields/)
  }
})
