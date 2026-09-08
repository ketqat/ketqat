"""CLI integration. Only the customer's local subprocess imports their factory."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from .regression import EXIT_CODES, Policy, Snapshot, capture, compare, load_json, not_executed, save_snapshot, write_private_text
from .regression_report import markdown, write_reports


def bounded_integer(minimum: int, maximum: int):
    def parse(value: str) -> int:
        try:
            number = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f'Use an integer from {minimum} to {maximum}.') from None
        if not minimum <= number <= maximum:
            raise argparse.ArgumentTypeError(f'Use an integer from {minimum} to {maximum}.')
        return number
    return parse


def case_identifier(value: str) -> str:
    if not 1 <= len(value) <= 120 or not re.fullmatch(r'[A-Za-z0-9_.-]+', value):
        raise argparse.ArgumentTypeError('Use a case ID of 1–120 letters, digits, underscores, dots or hyphens.')
    return value


def add_parser(subcommands):
    parser = subcommands.add_parser('regression', help='Local Qiskit regression checks; optional previewed private summary upload.')
    commands = parser.add_subparsers(dest='regression_command', required=True)
    run = commands.add_parser('capture', help='Execute your own local Python circuit factory with a time limit.')
    run.add_argument('factory', help='Local path.py:function returning QuantumCircuit. Runs your code locally.')
    run.add_argument('--case-id', type=case_identifier, required=True)
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--seed', type=bounded_integer(0, 2**32-1), default=42, metavar='0..4294967295')
    run.add_argument('--optimization-level', type=int, choices=range(4), default=1)
    run.add_argument('--shots', type=bounded_integer(1, 10_000_000), metavar='1..10000000', help='Optional ideal simulated sampling budget; omitted means exact probabilities.')
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
    # Fail before executing customer code if its evidence destination is unusable.
    args.output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
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
                    try:
                        if os.name == 'posix':
                            os.killpg(process.pid, signal.SIGKILL)
                        else:
                            process.kill()
                    except ProcessLookupError:
                        pass  # It exited between timeout and termination; still record timeout.
                    process.wait()
                    raise
            if code != 0 or not output.exists():
                exit_detail = f' (exit {code})' if code != 0 else ''
                snapshot = not_executed(args.case_id, 'ERROR', f'Local factory process failed{exit_detail} without a valid snapshot; check local disk space, permissions and capture size.')
            else:
                snapshot = Snapshot.model_validate(load_json(output))
        except subprocess.TimeoutExpired:
            snapshot = not_executed(args.case_id, 'ERROR', f'Capture timed out after {args.timeout} seconds.')
        except (OSError, ValueError):
            # A worker can exit successfully after writing a partial, oversized,
            # or invalid snapshot. Preserve portable failure evidence without
            # copying private file contents or validation details into it.
            snapshot = not_executed(args.case_id, 'ERROR',
                'Local capture could not produce a valid snapshot; check local disk space, permissions, capture size and factory behavior.')
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
            args.output_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
            try:
                from qiskit import QuantumCircuit
            except ImportError:
                b = not_executed('intentional-bell-mutation', 'NOT_RUN', 'Qiskit is unavailable. Install the pinned regression requirements.')
                c = b.model_copy(deep=True)
            else:
                baseline = QuantumCircuit(2)
                baseline.h(0)
                baseline.cx(0,1)
                candidate = QuantumCircuit(2)
                candidate.h(0)  # Deliberate removal of entanglement, not an SDK bug.
                b, c = capture(baseline, case_id='intentional-bell-mutation'), capture(candidate, case_id='intentional-bell-mutation')
            save_snapshot(b, args.output_dir / 'baseline.json')
            save_snapshot(c, args.output_dir / 'candidate.json')
            policy = Policy(resources={'two_qubit_gates': {}}, max_total_variation=0.05)
            write_private_text(args.output_dir / 'policy.json', policy.model_dump_json(indent=2) + '\n')
            report = compare(b, c, policy)
            report['sample'] = ('Intentional missing-CX mutation. Measured local simulation; not an observed Qiskit defect or customer incident.'
                                if b.status == c.status == 'EXECUTED' else 'Intentional missing-CX example was not fully executed; inspect capture status. No successful simulation is claimed.')
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
            from .regression_upload import RegressionUploadError
            # Only authored transport errors (including subclasses) are safe to
            # display. Arbitrary ValueError/validation details can contain input.
            file_errors = {
                FileNotFoundError: 'An input file or output directory was not found. Check the local paths and generate the required report or preview first.',
                PermissionError: 'A local file or directory is not accessible. Check its read/write permissions before retrying.',
                IsADirectoryError: 'A file path refers to a directory. Select the local report or preview file instead.',
            }
            message = str(exc) if isinstance(exc, RegressionUploadError) else file_errors.get(type(exc), type(exc).__name__)
            prefix = 'PREVIEW: FAILED. UPLOAD: NOT_REQUESTED' if args.regression_command == 'preview' else 'UPLOAD: FAILED'
            print(f'{prefix}. {message}. Local comparison verdict is unchanged.', file=sys.stderr)
        else:
            print(f'ERROR: {type(exc).__name__}. No successful report was produced. Check input schema, file paths and output-directory uniqueness.', file=sys.stderr)
        return EXIT_CODES['ERROR']


if __name__ == '__main__':
    worker(sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
           None if sys.argv[6] == 'None' else int(sys.argv[6]))
