"""Opt-in transport. Build an allowlist from local evidence; never upload source."""
from __future__ import annotations

import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from jsonschema import Draft7Validator

from .regression import Policy, Snapshot, compare, load_json

MAX_UPLOAD_BYTES = 100 * 1024


class RegressionUploadError(ValueError):
    """An authored, safe-to-display error; never includes input or response values."""


def _strict_json(payload: bytes, label: str):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise RegressionUploadError(f'{label} contains duplicate JSON keys.')
            value[key] = item
        return value

    def reject_constant(_):
        raise RegressionUploadError(f'{label} contains non-finite JSON.')

    try:
        return json.loads(payload, object_pairs_hook=unique, parse_constant=reject_constant)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise RegressionUploadError(f'{label} is not valid JSON. No response or input contents are displayed.') from None


def validate_summary(payload: dict) -> None:
    schema = json.loads(files('ketqat_runner').joinpath('schemas/regression-summary.schema.json').read_text())
    Draft7Validator(schema).validate(payload)


def prepare_summary(local_report: dict) -> dict:
    """Recompute from the local snapshots, then copy only enumerated fields."""
    baseline = Snapshot.model_validate(local_report['baseline'])
    candidate = Snapshot.model_validate(local_report['candidate'])
    policy = Policy.model_validate(local_report['policy'])
    report = compare(baseline, candidate, policy)
    if report['verdict'] != local_report['verdict'] or report['exit_code'] != local_report['exit_code']:
        raise RegressionUploadError('The local report verdict differs from its recorded evidence.')
    selected = set(policy.resources)
    stopped = report['verdict'] in ('ERROR', 'NOT_RUN', 'INCOMPATIBLE')

    def resources(snapshot):
        if stopped or snapshot.resources is None or not selected:
            return None
        return {key: value for key, value in snapshot.resources.model_dump().items() if key in selected}

    distribution = None
    for check in report['checks']:
        if check['metric'] == 'total_variation' and 'estimate' in check:
            exact = baseline.probabilities is not None and candidate.probabilities is not None
            distribution = {
                'estimate': min(1.0, check['estimate']),
                'method': 'EXACT_IDEAL' if exact else 'HOEFFDING_ALL_OUTCOMES',
                'qubits': baseline.conditions.qubits,
                'baseline_shots': None if exact else baseline.conditions.shots,
                'candidate_shots': None if exact else candidate.conditions.shots,
            }
    summary = {
        'schema_version': 'ketqat.regression.summary.v1', 'provenance': 'CLIENT_REPORTED',
        'case_key': hashlib.sha256(candidate.case_id.encode()).hexdigest(),
        'baseline_sha256': report['baseline_sha256'], 'candidate_sha256': report['candidate_sha256'],
        'baseline_status': baseline.status, 'candidate_status': candidate.status,
        'policy': policy.model_dump(), 'changed_fields': [x['field'] for x in report['changes']],
        'resources': {'baseline': resources(baseline), 'candidate': resources(candidate)},
        'distribution': distribution, 'verdict': report['verdict'], 'exit_code': report['exit_code'],
    }
    validate_summary(summary)
    return summary


def preview(report_path: Path, output: Path) -> str:
    summary = prepare_summary(load_json(report_path))
    payload = (json.dumps(summary, indent=2, allow_nan=False) + '\n').encode()
    if len(payload) > MAX_UPLOAD_BYTES:
        raise RegressionUploadError('Preview exceeds the 100 KiB upload limit.')
    # Private by default. Preview files still contain metrics and stable hashes.
    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(payload)
    fingerprint = hashlib.sha256(payload).hexdigest()
    print(f'PREVIEW_READY: {output}. Open this file before uploading.')
    print('Includes selected metrics, policy, changed field names and stable hashes. Hashes are not anonymization.')
    print('Excludes source, circuits, raw measurements, paths, case/repository names and environment values.')
    print(f'SHA256: {fingerprint}')
    print(f'COMPARISON: {summary["verdict"]} (CI exit {summary["exit_code"]}); UPLOAD: NOT_REQUESTED')
    return fingerprint


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the scoped credential to a redirected host/path.
        return None


def upload(summary_path: Path, confirmed_sha256: str, repository_id: str, server: str,
           *, opener=None, sleep=time.sleep) -> dict:
    if summary_path.stat().st_size > MAX_UPLOAD_BYTES:
        raise RegressionUploadError('Summary exceeds 100 KiB.')
    payload = summary_path.read_bytes()
    if not re.fullmatch(r'[a-f0-9]{64}', confirmed_sha256) or hashlib.sha256(payload).hexdigest() != confirmed_sha256:
        raise RegressionUploadError('Review the exact preview file and pass its SHA256; file changed or confirmation missing.')
    summary = _strict_json(payload, 'Confirmed summary')
    validate_summary(summary)
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,80}', repository_id):
        raise RegressionUploadError('Use the repository ID from your private workspace.')
    origin = urlsplit(server)
    if origin.username or origin.password or origin.query or origin.fragment or origin.path not in ('', '/'):
        raise RegressionUploadError('Server must be an origin with no credentials, query or path.')
    if origin.scheme != 'https' and not (origin.scheme == 'http' and origin.hostname in ('127.0.0.1', 'localhost', '::1')):
        raise RegressionUploadError('Uploads require HTTPS; HTTP is allowed only for a local development server.')
    if not origin.hostname:
        raise RegressionUploadError('Missing server hostname.')
    token = os.environ.get('KETQAT_REGRESSION_TOKEN', '')
    if not re.fullmatch(r'kqr_[A-Za-z0-9_-]{43}', token):
        raise RegressionUploadError('Set a scoped KETQAT_REGRESSION_TOKEN in the environment; never pass it on the command line.')
    endpoint = server.rstrip('/') + f'/api/regression/repositories/{repository_id}/reports'
    opener = opener or build_opener(NoRedirect())
    for attempt in range(3):
        request = Request(endpoint, data=payload, method='POST', headers={
            'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
            'Idempotency-Key': confirmed_sha256,
        })
        try:
            with opener.open(request, timeout=10) as response:
                body = response.read(8193)
                if len(body) > 8192:
                    raise RegressionUploadError('Unexpected upload response size.')
                result = _strict_json(body, 'Server acknowledgement')
                if not isinstance(result, dict):
                    raise RegressionUploadError('Server acknowledgement must be a JSON object.')
                if (result.get('upload') not in ('STORED', 'DUPLICATE') or
                    result.get('verdict') != summary['verdict'] or
                    not re.fullmatch(r'[A-Za-z0-9_-]{8,80}', result.get('report_id', ''))):
                    raise RegressionUploadError('Server did not acknowledge the report and original verdict.')
                return {key: result[key] for key in ('upload', 'verdict', 'report_id')}
        except HTTPError as error:
            code = error.code
            error.close()
            if code in (429, 502, 503, 504) and attempt < 2:
                sleep(2 ** (attempt + 1))
                continue
            guidance = {301: 'Redirect refused; use the actual API origin.', 302: 'Redirect refused; use the actual API origin.',
                        303: 'Redirect refused; use the actual API origin.', 307: 'Redirect refused; use the actual API origin.',
                        308: 'Redirect refused; use the actual API origin.', 401: 'Token missing, expired or revoked.', 403: 'Check token scope and active subscription.',
                        404: 'Repository unavailable to this credential.', 409: 'Review the active baseline and policy; re-run locally.',
                        413: 'Summary too large.', 422: 'Summary failed validation.',
                        429: 'Workspace usage or request limit reached.'}
            raise RegressionUploadError(f'UPLOAD_FAILED HTTP {code}: {guidance.get(code, "Service unavailable; keep the local report and retry later.")}') from None
        except (URLError, TimeoutError):
            if attempt < 2:
                sleep(2 ** (attempt + 1))
                continue
            raise RegressionUploadError('UPLOAD_FAILED: bounded network retries exhausted; local comparison remains valid.') from None
    raise RegressionUploadError('UPLOAD_FAILED: no acknowledgement.')
