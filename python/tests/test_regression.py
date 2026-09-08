"""Analytical fixtures + real Qiskit + malformed input + executable CLI tests."""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from qiskit import QuantumCircuit

from ketqat_runner.regression import (
    EXIT_CODES, Policy, ResourceLimit, Snapshot, capture, compare, load_json,
    not_executed, save_snapshot,
)
from ketqat_runner.regression_report import html_report


def bell():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def pair():
    return capture(bell(), case_id='bell'), capture(bell(), case_id='bell')


def amended(snapshot, **changes):
    return Snapshot.model_validate(snapshot.model_dump() | changes)


def test_analytical_bell_reference_and_deliberate_regression():
    # Independent reference: |Bell>=(|00>+|11>)/sqrt(2), not another call
    # through the capture implementation or Qiskit probabilities.
    b = capture(bell(), case_id='bell')
    assert b.status == 'EXECUTED', b.reason
    assert b.probabilities.get('00') == pytest.approx(0.5)
    assert b.probabilities.get('11') == pytest.approx(0.5)
    assert sum(v for k, v in b.probabilities.items() if k not in {'00','11'}) < 1e-12
    qc = QuantumCircuit(2)
    qc.h(0)
    c = capture(qc, case_id='bell')
    report = compare(b, c, Policy(max_total_variation=0.05))
    assert report['verdict'] == 'REGRESSION'
    # Bell vs |+0> differs by exactly 1/2 in total variation.
    assert report['checks'][0]['estimate'] == pytest.approx(0.5)
    assert report['exit_code'] == 1


def test_real_resource_regression_and_tolerated_variation():
    b = capture(QuantumCircuit(2), case_id='resource')
    qc = QuantumCircuit(2)
    qc.cx(0,1)
    c = capture(qc, case_id='resource')
    strict = Policy(resources={'two_qubit_gates': ResourceLimit()})
    relaxed = Policy(resources={'two_qubit_gates': ResourceLimit(absolute_increase=1)})
    assert compare(b,c,strict)['verdict'] == 'REGRESSION'
    assert compare(b,c,relaxed)['verdict'] == 'WITHIN_POLICY'


def test_rotation_reference_allows_small_probability_change():
    qc = QuantumCircuit(1)
    qc.ry(0.02, 0)
    b = capture(QuantumCircuit(1), case_id='rotation')
    c = capture(qc, case_id='rotation')
    report = compare(b,c,Policy(max_total_variation=0.001))
    assert report['checks'][0]['estimate'] == pytest.approx(math.sin(0.01)**2)
    assert report['verdict'] == 'WITHIN_POLICY'


def test_six_verdicts_have_nonzero_codes_except_within_policy():
    b,c = pair()
    p = Policy(max_total_variation=0.05)
    reports = [compare(b,c,p), compare(b,amended(c, probabilities={'00':1.0}),p),
               compare(b,amended(c, probabilities=None),p),
               compare(b,amended(c, conditions=c.conditions.model_dump() | {'seed':100}),p),
               compare(b,not_executed('bell','ERROR','execution failed'),p),
               compare(b,not_executed('bell','NOT_RUN','unsupported'),p)]
    assert {r['verdict'] for r in reports} == set(EXIT_CODES)
    for r in reports:
        assert r['exit_code'] == EXIT_CODES[r['verdict']]
        assert (r['exit_code'] == 0) == (r['verdict'] == 'WITHIN_POLICY')


def test_sdk_axis_allowed_only_when_explicit_and_never_hides_environment():
    b,c=pair()
    c=amended(c,environment=c.environment | {'qiskit':'2.999.test'})
    assert compare(b,c,Policy(max_total_variation=0.1))['verdict'] == 'INCOMPATIBLE'
    policy=Policy(changed_axes=['qiskit'],max_total_variation=0.1)
    assert compare(b,c,policy)['verdict'] == 'WITHIN_POLICY'
    c=amended(c,environment=c.environment | {'numpy':'other'})
    assert compare(b,c,policy)['verdict'] == 'INCOMPATIBLE'


def test_changed_circuit_is_incompatible_when_only_sdk_is_intended():
    b,c=pair()
    c=amended(c,circuit=None,circuit_sha256='a'*64)
    assert compare(b,c,Policy(changed_axes=['qiskit'],max_total_variation=0.1))['verdict'] == 'INCOMPATIBLE'


def test_no_global_phase_equivalence_claim():
    b,c=pair()
    qc=bell()
    qc.z(0)  # Orthogonal Bell state, identical Z-basis distribution.
    c=capture(qc,case_id='bell')
    report=compare(b,c,Policy(max_total_variation=0.01))
    assert report['verdict'] == 'WITHIN_POLICY'
    assert 'not program equivalence' in report['scope']


def test_small_shot_budget_inconclusive_even_if_zero_failures():
    b=capture(QuantumCircuit(1),case_id='shots',shots=10)
    c=capture(QuantumCircuit(1),case_id='shots',shots=10)
    report=compare(b,c,Policy(max_total_variation=0.05))
    assert report['verdict'] == 'INCONCLUSIVE'
    assert report['checks'][0]['upper'] > 0.05


def test_all_outcomes_including_unseen_are_in_family_bound():
    b=capture(QuantumCircuit(2),case_id='shots',shots=100_000)
    r=compare(b,b,Policy(max_total_variation=0.05,family_alpha=0.01))
    # K=4 even though only 00 was observed. Independent algebraic reference.
    expected=4*math.sqrt(math.log(1600)/(2*100_000))
    assert r['checks'][0]['upper'] == pytest.approx(expected)
    assert r['verdict'] == 'WITHIN_POLICY'


def test_samples_with_separated_distributions_regress():
    b=capture(QuantumCircuit(1),case_id='shots',shots=100_000)
    qc=QuantumCircuit(1)
    qc.x(0)
    c=capture(qc,case_id='shots',shots=100_000)
    assert compare(b,c,Policy(max_total_variation=0.05))['verdict'] == 'REGRESSION'


@pytest.mark.parametrize('mutation',[
    {'probabilities':{'00':float('nan')}}, {'probabilities':{'00':float('inf')}},
    {'probabilities':{'00':0.2}}, {'probabilities':{'0':1.0}},
    {'environment':{}}, {'resources':{'depth':True,'size':1,'two_qubit_gates':1}},
    {'circuit_sha256':'0'*64}, {'counts':{'00':5}}, {'status':'ERROR'},
])
def test_invalid_or_forged_records_never_pass(mutation):
    b,_=pair()
    with pytest.raises(ValidationError):
        amended(b,**mutation)


def test_duplicate_json_key_rejected(tmp_path):
    p=tmp_path/'duplicate.json'
    p.write_text('{"status":"ERROR","status":"EXECUTED"}')
    with pytest.raises(ValueError,match='Duplicate'):
        load_json(p)


def test_unsupported_measurements_and_custom_gate_not_run():
    qc=QuantumCircuit(2,2)
    qc.measure(0,1)
    qc.measure(1,0)
    assert capture(qc,case_id='map').status == 'NOT_RUN'
    qc=QuantumCircuit(1,1)
    qc.measure(0,0)
    qc.h(0)
    assert capture(qc,case_id='mid').status == 'NOT_RUN'
    qc=QuantumCircuit(1)
    custom=QuantumCircuit(1)
    custom.x(0)
    qc.append(custom.to_gate(label='not-a-standard-gate'),[0])
    assert capture(qc,case_id='custom').status == 'NOT_RUN'


def test_final_measurements_work_and_baseline_cannot_overwrite(tmp_path):
    qc=bell()
    qc.measure_all()
    b=capture(qc,case_id='bell')
    assert b.status == 'EXECUTED'
    path=tmp_path/'baseline.json'
    save_snapshot(b,path)
    original=path.read_bytes()
    with pytest.raises(FileExistsError):
        save_snapshot(b,path)
    assert original == path.read_bytes()
    assert Snapshot.model_validate(load_json(path)) == b


def cli(*args,env=None):
    return subprocess.run([sys.executable,'-c','from ketqat_runner.cli import main; raise SystemExit(main())',
                           'regression',*map(str,args)],capture_output=True,text=True,env=env,timeout=30)


def test_real_factory_cli_comparison_and_actions_summary(tmp_path):
    factory=tmp_path/'factory.py'
    factory.write_text('from qiskit import QuantumCircuit\ndef circuit():\n    return QuantumCircuit(1)\n')
    for side in ('baseline','candidate'):
        r=cli('capture',f'{factory}:circuit','--case-id','test','--output',tmp_path/f'{side}.json')
        assert r.returncode == 0,r.stderr+r.stdout
    policy=tmp_path/'policy.json'
    policy.write_text(Policy(max_total_variation=0.01).model_dump_json())
    env=dict(os.environ,GITHUB_STEP_SUMMARY=str(tmp_path/'summary.md'))
    r=cli('compare',tmp_path/'baseline.json',tmp_path/'candidate.json','--policy',policy,'--output-dir',tmp_path/'report',env=env)
    assert r.returncode == 0,r.stderr+r.stdout
    report=json.loads((tmp_path/'report/report.json').read_text())
    assert report['verdict'] == 'WITHIN_POLICY'
    assert 'WITHIN_POLICY' in (tmp_path/'summary.md').read_text()
    assert (tmp_path/'report/report.html').exists()


def test_factory_failure_and_timeout_are_not_green_and_secrets_not_logged(tmp_path):
    factory=tmp_path/'bad.py'
    factory.write_text('def circuit():\n    raise RuntimeError("secret-string-do-not-log")\n')
    r=cli('capture',f'{factory}:circuit','--case-id','bad','--output',tmp_path/'error.json')
    assert r.returncode == EXIT_CODES['ERROR']
    assert 'secret-string-do-not-log' not in r.stdout+r.stderr+(tmp_path/'error.json').read_text()
    factory.write_text('import time\ndef circuit():\n    time.sleep(30)\n')
    r=cli('capture',f'{factory}:circuit','--case-id','slow','--timeout','1','--output',tmp_path/'slow.json')
    assert r.returncode == EXIT_CODES['ERROR']
    assert 'timed out' in (tmp_path/'slow.json').read_text()


def test_sample_runs_real_simulation_and_returns_regression(tmp_path):
    r=cli('sample','--output-dir',tmp_path/'sample')
    assert r.returncode == EXIT_CODES['REGRESSION'],r.stderr+r.stdout
    report=json.loads((tmp_path/'sample/report/report.json').read_text())
    assert report['verdict'] == 'REGRESSION'
    assert 'Intentional' in report['sample']


def test_html_escapes_private_data():
    b,c=pair()
    report=compare(b,c,Policy(max_total_variation=0.1))
    page=html_report(report,{'unsafe':'</pre><script>alert(1)</script>'},c.model_dump())
    assert '<script>' not in page
    assert '&lt;script&gt;' in page
    assert "default-src 'none'" in page
