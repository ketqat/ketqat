"""Real captures across Python/TypeScript; actual bounded loopback HTTP transport."""
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading

import pytest
from qiskit import QuantumCircuit

from ketqat_runner.regression import Policy, Snapshot, capture, compare, not_executed
from ketqat_runner.regression_upload import prepare_summary, preview, upload


def reports():
    q = QuantumCircuit(2)
    q.h(0)
    q.cx(0, 1)
    b = capture(q, case_id='private-customer-case')
    c = capture(QuantumCircuit(2), case_id=b.case_id)
    policy = Policy(resources={'two_qubit_gates': {}}, max_total_variation=.05)
    missing = Snapshot.model_validate(b.model_dump() | {'resources': None, 'probabilities': None})
    incompatible = Snapshot.model_validate(b.model_dump() | {'environment': b.environment | {'python': '3.12'}})
    sampled = capture(q, case_id=b.case_id, shots=20)
    return [
        compare(b, b, policy), compare(b, c, policy), compare(b, missing, policy),
        compare(b, incompatible, policy), compare(b, not_executed(b.case_id, 'ERROR', 'secret-error'), policy),
        compare(b, not_executed(b.case_id, 'NOT_RUN', 'secret-reason'), policy),
        compare(sampled, sampled, policy),
    ]


def test_allowlisted_summaries_keep_all_six_verdicts_and_match_typescript():
    originals = reports()
    summaries = [prepare_summary(x) for x in originals]
    assert {s['verdict'] for s in summaries} == {'WITHIN_POLICY', 'REGRESSION', 'INCONCLUSIVE', 'INCOMPATIBLE', 'ERROR', 'NOT_RUN'}
    serialized = json.dumps(summaries)
    for secret in ('private-customer-case', 'secret-error', 'secret-reason', 'probabilities', 'factory', 'recorded_at'):
        assert secret not in serialized
    root = Path(__file__).resolve().parents[2]
    # CI builds dist explicitly. Missing TypeScript verification is a failure.
    script = """
      import {inspectRegressionSummary} from './dist/index.js';
      let input=''; for await (const part of process.stdin) input+=part;
      console.log(JSON.stringify(JSON.parse(input).map(inspectRegressionSummary)));
    """
    result = subprocess.run(['node', '--input-type=module', '-e', script], input=serialized,
                            capture_output=True, text=True, cwd=root, check=True)
    inspected = json.loads(result.stdout)
    for local, hosted in zip(originals, inspected):
        assert hosted['summary']['verdict'] == local['verdict']
        assert hosted['summary']['exit_code'] == local['exit_code']
        assert len(hosted['checks']) == len(local['checks'])
        for left, right in zip(local['checks'], hosted['checks']):
            assert left['metric'] == right['metric'] and left['verdict'] == right['verdict']
            for field in ('baseline', 'candidate', 'maximum', 'estimate', 'lower', 'upper'):
                if field in left:
                    assert right[field] == pytest.approx(left[field], abs=1e-12)


def test_preview_recomputes_and_redacts_forged_report_fields(tmp_path):
    report = reports()[1]
    report['arbitrary'] = 'secret-source'
    report['changes'][0]['candidate'] = 'secret-repository'
    path = tmp_path / 'local.json'
    path.write_text(json.dumps(report))
    output = tmp_path / 'summary.json'
    fingerprint = preview(path, output)
    assert hashlib.sha256(output.read_bytes()).hexdigest() == fingerprint
    assert output.stat().st_mode & 0o077 == 0
    assert 'secret-' not in output.read_text()
    with pytest.raises(FileExistsError):
        preview(path, output)
    report['verdict'] = 'WITHIN_POLICY'
    with pytest.raises(ValueError, match='differs'):
        prepare_summary(report)


def test_real_http_retry_and_confirmation_keep_original_verdict(tmp_path, monkeypatch):
    summary = prepare_summary(reports()[1])
    path = tmp_path / 'summary.json'
    path.write_text(json.dumps(summary))
    fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setenv('KETQAT_REGRESSION_TOKEN', 'kqr_' + 'a' * 43)
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            received.append((self.path, self.headers.get('Authorization'),
                             self.headers.get('Idempotency-Key'), self.rfile.read(int(self.headers['Content-Length']))))
            self.send_response(503 if len(received) == 1 else 201)
            self.end_headers()
            self.wfile.write(json.dumps({'upload': 'STORED', 'verdict': 'REGRESSION', 'report_id': 'report-test-123'}).encode())

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        endpoint = f'http://127.0.0.1:{server.server_port}'
        with pytest.raises(ValueError, match='exact preview'):
            upload(path, '0' * 64, 'repository-test', endpoint)
        assert len(received) == 0
        waits = []
        result = upload(path, fingerprint, 'repository-test', endpoint, sleep=waits.append)
        assert result['upload'] == 'STORED' and result['verdict'] == 'REGRESSION'
        assert waits == [2] and len(received) == 2
        assert received[0] == received[1]
        assert received[0][0] == '/api/regression/repositories/repository-test/reports'
        assert received[0][1] == 'Bearer ' + os.environ['KETQAT_REGRESSION_TOKEN']
        assert received[0][2] == fingerprint
        for endpoint in ('http://example.com', 'https://example.com/path', 'https://user:secret@example.com'):
            with pytest.raises(ValueError):
                upload(path, fingerprint, 'repository-test', endpoint)
        assert len(received) == 2
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_redirect_does_not_forward_credential(tmp_path, monkeypatch):
    path = tmp_path / 'summary.json'
    path.write_text(json.dumps(prepare_summary(reports()[0])))
    fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setenv('KETQAT_REGRESSION_TOKEN', 'kqr_' + 'a' * 43)
    paths = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            paths.append(self.path)
            self.send_response(307)
            self.send_header('Location', '/credential-trap')
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(ValueError, match='HTTP 307'):
            upload(path, fingerprint, 'repository-test', f'http://127.0.0.1:{server.server_port}')
        assert paths == ['/api/regression/repositories/repository-test/reports']
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_ambiguous_server_acknowledgements_are_rejected(tmp_path, monkeypatch):
    from io import BytesIO
    from types import SimpleNamespace
    path = tmp_path / 'summary.json'
    path.write_text(json.dumps(prepare_summary(reports()[1])))
    fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setenv('KETQAT_REGRESSION_TOKEN', 'kqr_' + 'a' * 43)
    valid_fields = b'"upload":"STORED","verdict":"REGRESSION","report_id":"report-test-123"'
    for body in (b'{' + valid_fields + b',"verdict":"WITHIN_POLICY"}',
                 b'{' + valid_fields + b',"extra":NaN}', b'[]'):
        opener = SimpleNamespace(open=lambda *args, **kwargs: BytesIO(body))
        with pytest.raises(ValueError):
            upload(path, fingerprint, 'repository-test', 'https://ketqat.com', opener=opener)


def test_cli_reports_authored_json_failures_without_leaking_input(tmp_path, monkeypatch, capsys):
    from io import BytesIO
    from types import SimpleNamespace
    from ketqat_runner import regression_upload
    from ketqat_runner.regression_cli import run
    from ketqat_runner.regression_upload import RegressionUploadError

    path = tmp_path / 'summary.json'
    path.write_text(json.dumps(prepare_summary(reports()[1])))
    monkeypatch.setenv('KETQAT_REGRESSION_TOKEN', 'kqr_' + 'a' * 43)
    args = SimpleNamespace(regression_command='upload', summary=path,
        confirm_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        repository='repository-test', server='https://ketqat.com')
    for body in (b'', b'<html>private-processor-body</html>', b'\xffprivate-processor-body'):
        monkeypatch.setattr(regression_upload, 'build_opener', lambda *a: SimpleNamespace(open=lambda *a, **kw: BytesIO(body)))
        assert run(args) == 4
        error = capsys.readouterr().err
        assert 'Server acknowledgement is not valid JSON' in error
        assert 'private-processor-body' not in error and 'kqr_' not in error

    class SpecializedUploadError(RegressionUploadError):
        pass
    def authored(*args):
        raise SpecializedUploadError('Review the confirmed summary.')
    monkeypatch.setattr(regression_upload, 'upload', authored)
    assert run(args) == 4
    assert 'Review the confirmed summary.' in capsys.readouterr().err
    def untrusted(*args):
        raise ValueError('private-input-value')
    monkeypatch.setattr(regression_upload, 'upload', untrusted)
    assert run(args) == 4
    assert 'private-input-value' not in capsys.readouterr().err
