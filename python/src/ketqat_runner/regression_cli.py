"""CLI integration. Only the customer's local subprocess imports their factory."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from .regression import EXIT_CODES, Policy, Snapshot, capture, compare, load_json, not_executed, save_snapshot
from .regression_report import markdown, write_reports


def add_parser(subcommands):
    parser = subcommands.add_parser('regression', help='Local Qiskit regression checks; optional previewed private summary upload.')
    commands = parser.add_subparsers(dest='regression_command', required=True)
    run = commands.add_parser('capture', help='Execute your own local Python circuit factory with a time limit.')
    run.add_argument('factory', help='Local path.py:function returning QuantumCircuit. Runs your code locally.')
    run.add_argument('--case-id', required=True)
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--seed', type=int, default=42)
    run.add_argument('--optimization-level', type=int, choices=range(4), default=1)
    run.add_argument('--shots', type=int, help='Optional ideal simulated sampling budget; omitted means exact probabilities.')
    run.add_argument('--timeout', type=int, choices=range(1,301), metavar='1..300', default=60)
    diff = commands.add_parser('compare', help='Compare two local snapshots; never updates a baseline.')
    diff.add_argument('baseline', type=Path)
    diff.add_argument('candidate', type=Path)
    diff.add_argument('--policy', type=Path, required=True)
    diff.add_argument('--output-dir', type=Path, required=True)
    sample = commands.add_parser('sample', help='Execute a labelled intentional Bell-circuit mutation locally.')
    sample.add_argument('--output-dir', type=Path, required=True)
    preview = commands.add_parser('preview', help='Write an allowlisted summary for review; sends nothing.')
    preview.add_argument('report', type=Path)
    preview.add_argument('--output', type=Path, required=True)
    upload = commands.add_parser('upload', help='Send exactly the reviewed summary using a scoped environment token.')
    upload.add_argument('summary', type=Path)
    upload.add_argument('--confirm-sha256', required=True)
    upload.add_argument('--repository', required=True)
    upload.add_argument('--server', default='https://ketqat.com')


def worker(factory: str, case_id: str, output: Path, seed: int, level: int, shots: int | None):
    try:
        path, function = factory.rsplit(':', 1)
        path = Path(path).resolve(strict=True)
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location('ketqat_user_factory', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        snapshot = capture(getattr(module, function)(), case_id=case_id,
                           seed=seed, optimization_level=level, shots=shots)
        snapshot = Snapshot.model_validate(snapshot.model_dump() | {
            'factory': factory, 'factory_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    except Exception as exc:
        snapshot = not_executed(case_id, 'ERROR', f'Local factory failed ({type(exc).__name__}); inspect your factory locally.')
    try:
        save_snapshot(snapshot, output)
    except ValueError:
        save_snapshot(not_executed(case_id, 'ERROR',
            'Snapshot serialization or 2 MiB size limit failed; reduce the local circuit and retry.'), output)


def run_capture(args) -> int:
    if args.output.exists():
        raise ValueError('Output already exists; use a new path to preserve previous evidence.')
    with tempfile.TemporaryDirectory(prefix='ketqat-capture-') as temporary:
        output = Path(temporary) / 'snapshot.json'
        command = [sys.executable, '-m', 'ketqat_runner.regression_cli', args.factory, args.case_id,
                   str(output), str(args.seed), str(args.optimization_level), str(args.shots)]
        try:
            # Factory stdout/stderr may contain secrets; never copy to reports or
            # CI logs. A local factory is trusted user code, not a sandbox.
            with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  start_new_session=(os.name == 'posix')) as process:
                try:
                    code = process.wait(timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    if os.name == 'posix':
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait()
                    raise
            if code != 0 or not output.exists():
                snapshot = not_executed(args.case_id, 'ERROR', 'Local factory process failed without a valid snapshot; check local disk space, permissions and capture size.')
            else:
                snapshot = Snapshot.model_validate(load_json(output))
        except subprocess.TimeoutExpired:
            snapshot = not_executed(args.case_id, 'ERROR', f'Capture timed out after {args.timeout} seconds.')
        save_snapshot(snapshot, args.output)
    print(f'{snapshot.status}: {snapshot.reason or "Local snapshot written; no upload."}')
    return 0 if snapshot.status == 'EXECUTED' else EXIT_CODES[snapshot.status]


def run(args) -> int:
    try:
        if args.regression_command == 'preview':
            from .regression_upload import preview
            preview(args.report, args.output)
            return 0
        if args.regression_command == 'upload':
            from .regression_upload import upload
            result = upload(args.summary, args.confirm_sha256, args.repository, args.server)
            print(f'UPLOAD: {result["upload"]}; COMPARISON: {result["verdict"]}; report {result["report_id"]}')
            return 0
        if args.regression_command == 'capture':
            return run_capture(args)
        if args.regression_command == 'sample':
            from qiskit import QuantumCircuit
            args.output_dir.mkdir(parents=True, exist_ok=False)
            baseline = QuantumCircuit(2)
            baseline.h(0)
            baseline.cx(0,1)
            candidate = QuantumCircuit(2)
            candidate.h(0)  # Deliberate removal of entanglement, not an SDK bug.
            b, c = capture(baseline, case_id='intentional-bell-mutation'), capture(candidate, case_id='intentional-bell-mutation')
            save_snapshot(b, args.output_dir / 'baseline.json')
            save_snapshot(c, args.output_dir / 'candidate.json')
            policy = Policy(resources={'two_qubit_gates': {}}, max_total_variation=0.05)
            args.output_dir.joinpath('policy.json').write_text(policy.model_dump_json(indent=2) + '\n')
            report = compare(b, c, policy)
            report['sample'] = 'Intentional missing-CX mutation. Measured local simulation; not an observed Qiskit defect or customer incident.'
            write_reports(args.output_dir / 'report', report, b.model_dump(), c.model_dump())
            print(report['sample'])
        else:
            b, c = Snapshot.model_validate(load_json(args.baseline)), Snapshot.model_validate(load_json(args.candidate))
            policy = Policy.model_validate(load_json(args.policy))
            report = compare(b, c, policy)
            write_reports(args.output_dir, report, b.model_dump(), c.model_dump())
        print(f"{report['verdict']}: {report['conclusion']}")
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as handle:
                handle.write(markdown(report))
        return report['exit_code']
    except Exception as exc:
        # Validation exceptions can contain the invalid value (possibly private).
        if args.regression_command in ('upload', 'preview'):
            # Transport errors are deliberately authored, without server response bodies or credentials.
            message = str(exc) if type(exc) is ValueError else type(exc).__name__
            print(f'UPLOAD: FAILED_OR_NOT_REQUESTED. {message}. Local comparison verdict is unchanged.', file=sys.stderr)
        else:
            print(f'ERROR: {type(exc).__name__}. No successful report was produced. Check input schema, file paths and output-directory uniqueness.', file=sys.stderr)
        return EXIT_CODES['ERROR']


if __name__ == '__main__':
    worker(sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
           None if sys.argv[6] == 'None' else int(sys.argv[6]))
