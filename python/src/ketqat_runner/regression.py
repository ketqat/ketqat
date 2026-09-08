"""Local Qiskit regression records. No network, credentials or hosted execution.

Exact ideal output distributions, sampled output distributions and compiled
resource counts are distinct claims. None proves whole-program equivalence.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Verdict = Literal['WITHIN_POLICY', 'REGRESSION', 'INCONCLUSIVE', 'INCOMPATIBLE', 'ERROR', 'NOT_RUN']
EXIT_CODES = {'WITHIN_POLICY': 0, 'REGRESSION': 1, 'INCONCLUSIVE': 2,
              'INCOMPATIBLE': 3, 'ERROR': 4, 'NOT_RUN': 5}
METRICS = ('depth', 'size', 'two_qubit_gates')
MAX_FILE_BYTES = 2 * 1024 * 1024


class Record(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)


class Conditions(Record):
    execution: Literal['ideal_statevector', 'sampled_ideal'] = 'ideal_statevector'
    initial_state: Literal['zero'] = 'zero'
    measurement: Literal['all_qubits_computational_basis'] = 'all_qubits_computational_basis'
    bit_order: Literal['qiskit_msb_left'] = 'qiskit_msb_left'
    backend: Literal['qiskit.quantum_info.Statevector'] = 'qiskit.quantum_info.Statevector'
    noise: Literal['none'] = 'none'
    qubits: int = Field(ge=1, le=12)
    seed: int = Field(ge=0, le=2**32-1)
    shots: int | None = Field(default=None, ge=1, le=10_000_000)
    optimization_level: int = Field(ge=0, le=3)
    basis_gates: list[str] = Field(min_length=1, max_length=32)


class Resources(Record):
    depth: int = Field(ge=0, le=10_000_000)
    size: int = Field(ge=0, le=10_000_000)
    two_qubit_gates: int = Field(ge=0, le=10_000_000)


class Snapshot(Record):
    schema_version: Literal['ketqat.regression.snapshot.v1'] = 'ketqat.regression.snapshot.v1'
    case_id: str = Field(min_length=1, max_length=120, pattern=r'^[A-Za-z0-9_.-]+$')
    status: Literal['EXECUTED', 'ERROR', 'NOT_RUN']
    reason: str | None = Field(default=None, max_length=500)
    recorded_at: str = Field(max_length=50)
    source_commit: str | None = Field(default=None, pattern=r'^[0-9a-f]{40,64}$')
    source_dirty: bool | None = None
    factory: str | None = Field(default=None, max_length=1000)
    factory_sha256: str | None = Field(default=None, pattern=r'^[0-9a-f]{64}$')
    environment: dict[str, str] = Field(max_length=20)
    conditions: Conditions | None = None
    circuit_sha256: str | None = Field(default=None, pattern=r'^[0-9a-f]{64}$')
    # These private local inputs are never implicitly sent to a hosted service.
    circuit: dict[str, Any] | None = None
    resources: Resources | None = None
    probabilities: dict[str, float] | None = Field(default=None, max_length=4096)
    counts: dict[str, int] | None = Field(default=None, max_length=4096)

    @model_validator(mode='after')
    def consistent(self):
        if self.status != 'EXECUTED':
            if not self.reason or self.resources is not None or self.probabilities is not None or self.counts is not None:
                raise ValueError('Non-execution needs a reason and cannot contain successful metrics.')
            return self
        if not self.conditions or not self.circuit_sha256:
            raise ValueError('Executed snapshots need conditions and a circuit fingerprint.')
        required = {'python', 'system', 'machine', 'kernel', 'ketqat_capture', 'qiskit', 'numpy', 'scipy', 'ketqat'}
        if set(self.environment) != required or any(not v or len(v) > 200 or v == 'not_installed' for v in self.environment.values()):
            raise ValueError('Executed snapshots require complete, bounded environment versions.')
        c = self.conditions
        if (c.execution == 'ideal_statevector') != (c.shots is None):
            raise ValueError('Shot budget must match the declared execution method.')
        if self.probabilities is not None and self.counts is not None:
            raise ValueError('Exact probabilities and sampled counts are distinct observations.')
        for values in (self.probabilities, self.counts):
            if values is not None:
                if not values or any(len(k) != c.qubits or set(k) - {'0', '1'} for k in values):
                    raise ValueError('Outcome labels must be full-width binary bitstrings.')
                if any(v < 0 for v in values.values()):
                    raise ValueError('Negative observations are invalid.')
        if self.probabilities is not None:
            if c.execution != 'ideal_statevector' or c.shots is not None:
                raise ValueError('Exact probabilities have no shots and require ideal_statevector.')
            if any(v > 1 for v in self.probabilities.values()) or not math.isclose(sum(self.probabilities.values()), 1, abs_tol=1e-9):
                raise ValueError('Probabilities must sum to one.')
        if self.counts is not None:
            if c.execution != 'sampled_ideal' or c.shots is None or sum(self.counts.values()) != c.shots:
                raise ValueError('Counts must sum to the declared sampled shot budget.')
        if self.circuit is not None and digest(self.circuit) != self.circuit_sha256:
            raise ValueError('Circuit fingerprint does not match local inputs.')
        return self


class ResourceLimit(Record):
    absolute_increase: int = Field(default=0, ge=0, le=10_000_000)
    relative_increase: float = Field(default=0.0, ge=0, le=1, description="Fractional increase: 0.1 means +10%, 1 means +100%.")


class Policy(Record):
    schema_version: Literal['ketqat.regression.policy.v1'] = 'ketqat.regression.policy.v1'
    # Only these axes can be intentionally changed. Noise/backend/measurement
    # and machine/runtime conditions never silently become equivalent.
    changed_axes: list[Literal['source_commit', 'circuit', 'qiskit']] = Field(default_factory=lambda: ['source_commit', 'circuit'], max_length=3)
    resources: dict[Literal['depth', 'size', 'two_qubit_gates'], ResourceLimit] = Field(default_factory=dict, max_length=3)
    max_total_variation: float | None = Field(default=None, ge=0, le=1)
    family_alpha: float = Field(default=0.01, gt=0, lt=1)

    @model_validator(mode='after')
    def useful(self):
        if not self.resources and self.max_total_variation is None:
            raise ValueError('Select at least one measured resource or distribution policy.')
        if len(set(self.changed_axes)) != len(self.changed_axes):
            raise ValueError('Changed axes must not repeat.')
        return self


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def environment() -> dict[str, str]:
    values = {'python': platform.python_version(), 'system': platform.system(),
              'machine': platform.machine(), 'kernel': platform.release(), 'ketqat_capture': '1'}
    for name in ('qiskit', 'numpy', 'scipy', 'ketqat'):
        try:
            values[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            values[name] = 'not_installed'
    return values


def provenance() -> dict[str, Any]:
    def git(*args):
        result = subprocess.run(['git', *args], capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else None
    try:
        commit, status = git('rev-parse', 'HEAD'), git('status', '--porcelain', '--untracked-files=no')
    except (OSError, subprocess.TimeoutExpired):
        commit, status = None, None
    return {'source_commit': commit, 'source_dirty': None if status is None else bool(status)}


def not_executed(case_id: str, status: Literal['ERROR', 'NOT_RUN'], reason: str) -> Snapshot:
    return Snapshot(case_id=case_id, status=status, reason=reason,
                    recorded_at=datetime.now(timezone.utc).isoformat(), environment=environment(), **provenance())


class UnsupportedCircuit(ValueError):
    pass


def capture(circuit: Any, *, case_id: str, seed: int = 42, optimization_level: int = 1,
            shots: int | None = None) -> Snapshot:
    """Add to an existing test: snapshot = capture(qc, case_id='my-case').

    Simulates |0...0> and full-register Z measurement after compilation to
    rx/ry/rz/cx. No timing, noise, hardware or whole-program equivalence claim.
    Unsupported inputs return NOT_RUN; execution errors return ERROR.
    """
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit.quantum_info import Statevector
    except ImportError:
        return not_executed(case_id, 'NOT_RUN', 'Install the regression extra with Qiskit 2.x.')
    try:
        if not importlib.metadata.version('qiskit').startswith('2.'):
            raise UnsupportedCircuit('This capture adapter supports Qiskit 2.x only.')
        if not isinstance(circuit, QuantumCircuit):
            raise UnsupportedCircuit('The factory must return a Qiskit QuantumCircuit.')
        if not 1 <= circuit.num_qubits <= 12 or len(circuit.data) > 100_000 or circuit.parameters:
            raise UnsupportedCircuit('Requires 1–12 qubits, at most 100000 instructions, and bound parameters.')
        c = Conditions(qubits=circuit.num_qubits, seed=seed, shots=shots,
                       execution='sampled_ideal' if shots is not None else 'ideal_statevector',
                       optimization_level=optimization_level, basis_gates=['rx', 'ry', 'rz', 'cx'])
        # Accept measurement-free circuits or one final identity mapping of
        # every qubit. Reject reordering/partial reads rather than hide them.
        measurements = [(circuit.find_bit(i.qubits[0]).index, circuit.find_bit(i.clbits[0]).index)
                        for i in circuit.data if i.operation.name == 'measure']
        if measurements and (circuit.num_clbits != c.qubits or sorted(measurements) != [(i, i) for i in range(c.qubits)]):
            raise UnsupportedCircuit('Only final all-qubit identity-mapped measurements are supported.')
        clean = circuit.remove_final_measurements(inplace=False)
        if any(i.operation.name in ('measure', 'reset', 'if_else', 'while_loop', 'for_loop', 'switch_case', 'delay')
               or getattr(i.operation, 'condition', None) is not None for i in clean.data):
            raise UnsupportedCircuit('Mid-circuit measurement, reset, timing and classical control are unsupported.')
        # Fingerprint input instructions BEFORE the transpiler. A Qiskit
        # upgrade is allowed to change the compiler output. User-named custom
        # gates need explicit decomposition; a name does not identify a matrix.
        for instruction in clean.data:
            operation = instruction.operation
            if operation.name != 'barrier' and not operation.base_class.__module__.startswith('qiskit.circuit.library.standard_gates.'):
                raise UnsupportedCircuit('Decompose custom gates into standard Qiskit gates before capture.')
        representation = {'qubits': c.qubits, 'measurement_map': [list(pair) for pair in measurements],
            'global_phase': float(clean.global_phase),
            'instructions': [{'gate': i.operation.name,
                              'qubits': [clean.find_bit(q).index for q in i.qubits],
                              'params': [float(p) for p in i.operation.params]} for i in clean.data]}
        compiled = transpile(clean, basis_gates=c.basis_gates,
                             optimization_level=optimization_level, seed_transpiler=seed)
        state = Statevector.from_instruction(compiled)
        resources = Resources(depth=compiled.depth(), size=compiled.size(),
                              two_qubit_gates=sum(len(i.qubits) == 2 and i.operation.name != 'barrier' for i in compiled.data))
        probs, counts = None, None
        if shots is None:
            probs = {str(k): float(v) for k, v in state.probabilities_dict().items()}
        else:
            state.seed(seed)
            counts = {str(k): int(v) for k, v in state.sample_counts(shots).items()}
        return Snapshot(case_id=case_id, status='EXECUTED', recorded_at=datetime.now(timezone.utc).isoformat(),
                        environment=environment(), conditions=c, circuit=representation,
                        circuit_sha256=digest(representation), resources=resources,
                        probabilities=probs, counts=counts, **provenance())
    except UnsupportedCircuit as exc:
        return not_executed(case_id, 'NOT_RUN', str(exc))
    except Exception as exc:
        # Provider/user exception strings can contain paths/tokens/source. Keep
        # only the exception type in the portable result; debug locally.
        return not_executed(case_id, 'ERROR', f'Qiskit capture failed ({type(exc).__name__}); reproduce locally to inspect the exception.')


def _differences(baseline: Snapshot, candidate: Snapshot) -> list[dict[str, Any]]:
    differences = []
    for field in ('source_commit', 'source_dirty', 'case_id', 'circuit_sha256', 'factory_sha256'):
        a, b = getattr(baseline, field), getattr(candidate, field)
        if a != b:
            differences.append({'field': field, 'baseline': a, 'candidate': b})
    for field in ('environment', 'conditions'):
        a = getattr(baseline, field)
        b = getattr(candidate, field)
        a = a.model_dump() if isinstance(a, BaseModel) else (a or {})
        b = b.model_dump() if isinstance(b, BaseModel) else (b or {})
        for key in sorted(set(a) | set(b)):
            if a.get(key) != b.get(key):
                differences.append({'field': f'{field}.{key}', 'baseline': a.get(key), 'candidate': b.get(key)})
    return differences


def compare(baseline: Snapshot, candidate: Snapshot, policy: Policy) -> dict[str, Any]:
    differences = _differences(baseline, candidate)
    allowed = {'source_commit': {'source_commit', 'source_dirty', 'factory_sha256'}, 'circuit': {'circuit_sha256'},
               'qiskit': {'environment.qiskit'}}
    permitted = set().union(*(allowed[axis] for axis in policy.changed_axes))
    for difference in differences:
        difference['intentional'] = difference['field'] in permitted
    report = {'schema_version': 'ketqat.regression.report.v1', 'case_id': candidate.case_id,
              'baseline_sha256': digest(baseline.model_dump()), 'candidate_sha256': digest(candidate.model_dump()),
              'policy': policy.model_dump(), 'changes': differences, 'checks': [],
              'baseline': baseline.model_dump(), 'candidate': candidate.model_dump(),
              'scope': 'Declared compiled-resource policy and selected |0> computational-basis output only; not program equivalence, speed, cost or hardware correctness.',
              'next_steps': [], 'upload': 'NOT_REQUESTED'}

    def finish(verdict: Verdict, reason: str, next_step: str):
        report.update(verdict=verdict, exit_code=EXIT_CODES[verdict], conclusion=reason,
                      next_steps=[next_step])
        return report

    if baseline.case_id != candidate.case_id:
        return finish('INCOMPATIBLE', 'Case identities differ.', 'Compare captures of the same test case.')
    if baseline.status != 'EXECUTED':
        return finish('ERROR' if baseline.status == 'ERROR' else 'NOT_RUN',
                      f'Baseline {baseline.status}: {baseline.reason}', 'Produce and review a valid baseline first.')
    if candidate.status != 'EXECUTED':
        return finish('ERROR' if candidate.status == 'ERROR' else 'NOT_RUN',
                      f'Candidate {candidate.status}: {candidate.reason}', 'Reproduce the capture locally; no baseline was updated.')
    if any(not d['intentional'] for d in differences):
        return finish('INCOMPATIBLE', 'A fixed comparison condition changed.',
                      'Restore fixed conditions or explicitly select a supported changed axis; inspect every difference.')
    checks = report['checks']
    for metric, limit in policy.resources.items():
        if baseline.resources is None or candidate.resources is None:
            checks.append({'metric': metric, 'verdict': 'INCONCLUSIVE', 'reason': 'Resource observation missing.'})
            continue
        a, b = getattr(baseline.resources, metric), getattr(candidate.resources, metric)
        bound = a * (1 + limit.relative_increase) + limit.absolute_increase
        checks.append({'metric': metric, 'baseline': a, 'candidate': b, 'maximum': bound,
                       'verdict': 'WITHIN_POLICY' if b <= bound else 'REGRESSION',
                       'method': 'deterministic compiled count; user policy'})
    if policy.max_total_variation is not None:
        tolerance = policy.max_total_variation
        a, b = baseline.probabilities, candidate.probabilities
        method = 'exact ideal probabilities (floating-point); no statistical claim'
        radius = 0.0
        if a is None or b is None:
            if baseline.counts is not None and candidate.counts is not None:
                n, m = baseline.conditions.shots, candidate.conditions.shots
                a = {k: v/n for k, v in baseline.counts.items()}
                b = {k: v/m for k, v in candidate.counts.items()}
                k = 2**baseline.conditions.qubits
                # Hoeffding + union bound over both samples and ALL K outcomes,
                # including unobserved outcomes. Simultaneous report-level bound.
                radius = 0.5 * k * (math.sqrt(math.log(4*k/policy.family_alpha)/(2*n)) +
                                   math.sqrt(math.log(4*k/policy.family_alpha)/(2*m)))
                method = 'Hoeffding simultaneous total-variation bound over all outcomes and both samples'
            else:
                a, b = None, None
        if a is None or b is None:
            checks.append({'metric': 'total_variation', 'verdict': 'INCONCLUSIVE', 'reason': 'Distribution observation missing.'})
        else:
            tv = 0.5 * sum(abs(a.get(k, 0)-b.get(k, 0)) for k in set(a) | set(b))
            low, high = max(0.0, tv-radius), min(1.0, tv+radius)
            verdict = 'WITHIN_POLICY' if high <= tolerance else ('REGRESSION' if low > tolerance else 'INCONCLUSIVE')
            checks.append({'metric': 'total_variation', 'estimate': tv, 'lower': low, 'upper': high,
                           'maximum': tolerance, 'method': method, 'family_alpha': policy.family_alpha if radius else None,
                           'verdict': verdict})
    if any(c['verdict'] == 'REGRESSION' for c in checks):
        return finish('REGRESSION', 'At least one declared policy limit is exceeded.',
                      'Inspect failing metrics and intentional changes; do not promote this candidate automatically.')
    if not checks or any(c['verdict'] == 'INCONCLUSIVE' for c in checks):
        return finish('INCONCLUSIVE', 'The available data cannot establish that every selected check is within policy.',
                      'Supply missing observations or increase the predeclared shot budget; repeated testing changes error risk.')
    return finish('WITHIN_POLICY', 'All selected checks are within the declared policy under the recorded conditions.',
                  'Review the changes and scientific scope before merging; this is not a correctness certificate.')


def load_json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('Input exceeds the 2 MiB local file limit.')
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate JSON keys are invalid.')
            value[key] = item
        return value
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON is invalid.')))


def save_snapshot(snapshot: Snapshot, path: Path) -> None:
    # Never overwrite a baseline/candidate implicitly. Local filesystem/Git
    # permissions govern these files; team approval is a hosted responsibility.
    payload = snapshot.model_dump_json(indent=2) + '\n'
    if len(payload.encode('utf-8')) > MAX_FILE_BYTES:
        raise ValueError('Snapshot exceeds the 2 MiB local file limit; reduce the test circuit.')
    with path.open('x', encoding='utf-8') as handle:
        handle.write(payload)
