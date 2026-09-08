# Catch a Qiskit regression locally

For developers reviewing circuit changes and Qiskit 2.x upgrades. Your Python
code runs on your machine or your CI runner. This free flow uses no account,
network upload, QPU, GPU or language model. Customer CI compute charges are
separate from any future KetQat subscription.

## Install from this repository

The source installation below targets merged `main`, without requiring a PyPI
or npm release. For an unmerged review, check out that review's exact commit
first. Record `git rev-parse HEAD` and pin the reviewed commit in CI.

```bash
git clone https://github.com/ketqat/ketqat-sdk.git
cd ketqat-sdk
git rev-parse HEAD
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-regression-py311.txt
python -m pip install --require-hashes -r requirements-regression-build-py311.txt
python -m pip install --no-build-isolation --no-deps ./python
ketqat regression sample --output-dir sample
```

The build-backend lock pins Hatchling and its dependencies as well as the
runtime lock. `--no-build-isolation` prevents an implicit, unpinned build-backend
download. These locks target Python 3.11; record the interpreter and source
commit alongside your report.

**Expected exit: 1 (REGRESSION).** This is a deliberately removed CX gate from a
Bell circuit, executed with real ideal simulation. It is not a reported Qiskit
bug. Open `sample/report/report.html`; its measured total-variation distance
should be approximately 0.5. JSON and GitHub Actions Markdown are alongside it.
The sample is a check of the product, not customer adoption or hardware evidence.

Resource limits use `absolute_increase` in gate/depth units and
`relative_increase` as a fraction from 0 to 1: `0.1` means +10%, `1` means +100%.
Both allowances are added to the baseline; the total is an upper limit.

## Add one call to your existing Python test

```python
from ketqat_runner.regression import capture, save_snapshot
from pathlib import Path

# qc is your existing Qiskit QuantumCircuit.
snapshot = capture(qc, case_id="prepare-state", seed=42, optimization_level=1)
save_snapshot(snapshot, Path("candidate.json"))
assert snapshot.status == "EXECUTED", snapshot.reason
```

Alternatively expose a function returning your existing circuit, then run:

```bash
ketqat regression capture tests/circuits.py:prepare_state \
  --case-id prepare-state --output baseline.json
# Check out / edit the candidate while keeping baseline.json unchanged.
ketqat regression capture tests/circuits.py:prepare_state \
  --case-id prepare-state --output candidate.json
ketqat regression compare baseline.json candidate.json \
  --policy examples/regression/policy.json --output-dir change-report
```

Factory import and execution happen in a local child process (60-second default,
1–300 seconds configurable). This is your code, not a security sandbox; do not
run unknown factories. Files/directories must be new to avoid stale reports or
silent baseline replacement. Store local baselines in your own protected Git
branch. The hosted team approval/history flow is tracked separately and is not
claimed available by this local command.

The supplied policy permits circuit and source changes, accepts up to one extra
two-qubit gate and up to 0.05 total variation. Change these limits to match your
actual test. For a Qiskit-only upgrade use `changed_axes: ["qiskit"]` in JSON,
keep the source and circuit fixed, and install the two Qiskit versions into
otherwise identical environments. A changed dependency version is recorded and
is allowed only for Qiskit when that axis is selected. Noise, backend, machine,
Python, other dependencies, seed, shots and transpiler configuration remain fixed.

## What the results mean

| Verdict | Exit | Next action |
| --- | --- | --- |
| WITHIN_POLICY | 0 | All selected observations fit this policy; review scope |
| REGRESSION | 1 | Inspect exceeded limits; never auto-promote the candidate |
| INCONCLUSIVE | 2 | Supply missing data or revise the predeclared sample budget |
| INCOMPATIBLE | 3 | Restore fixed conditions or select a supported change axis |
| ERROR | 4 | Capture/process/input/output failed; investigate locally |
| NOT_RUN | 5 | Unsupported circuit or missing dependency; no successful execution |

The report contains conclusion, impact, checks, changed conditions, policy and
both snapshots. HTML is offline, uses no scripts and escapes data. Its raw
details contain local circuit instructions, versions and potentially private
paths/test names. **Inspect before sharing.** Nothing is uploaded automatically.
If `GITHUB_STEP_SUMMARY` is set, the CLI appends its concise result there; CI
must honor its exit code. Do not add `|| true` or call uncertainty success.

## Scientific scope and limits

Supported: Qiskit 2.x, 1–12 qubits, at most 100,000 instructions, bound standard
gates, no measurements or final full-register identity-mapped measurement.
Decompose custom gates explicitly. Mid-circuit measurement, reset, classical
control, delay/noise and hardware are not supported. Captures compile to
`rx`, `ry`, `rz`, `cx` with the recorded seed/optimization level and no coupling
constraint. A two-qubit count is not physical device cost or runtime.

The default calculates the compiled circuit's ideal probabilities on input
`|0...0>` in the computational basis using Qiskit's Statevector. Shots are null,
not fabricated. This cannot detect every phase error, certify circuit equivalence,
prove whole-program correctness or measure execution speed.

With `--shots N`, ideal samples replace exact probabilities. The comparison
reports a simultaneous Hoeffding/union bound on total variation over both samples
and **all** possible output bins, including unobserved outcomes. `family_alpha`
(default 0.01) is the upper error budget for that report's distribution interval.
Intervals wholly below tolerance are WITHIN_POLICY, wholly above are REGRESSION,
and overlaps are INCONCLUSIVE. This conservative method becomes uninformative
quickly as qubits increase. Use exact ideal probabilities where appropriate.
Zero observed failures do not imply zero true failure probability.

Repeated reports are not covered by one lifetime error budget. Predeclare a
budget across planned comparisons (for R reports, alpha/R is a simple
Bonferroni allocation); repeatedly sampling until a favourable result invalidates
that interpretation. Seed matching is reproducibility metadata, not a substitute
for these bounds. Resource-count limits are deterministic policy checks, not
statistical or equivalence tests. A matching record hash is integrity only.

Useful alternatives: [Qiskit Statevector](https://quantum.cloud.ibm.com/docs/en/api/qiskit/quantum_info.Statevector),
[MQT QCEC](https://mqt.readthedocs.io/projects/qcec/en/latest/) for circuit
equivalence, and [QuCheck](https://github.com/GabrielPontolillo/qucheck) for
property-based testing. These tools solve different verification claims.

## Troubleshooting

- `ERROR` with a factory exception: run your factory locally to see its exception;
  the report intentionally excludes exception strings that might contain secrets.
- `ERROR` before capture: verify JSON schemas, paths, Python version and that the
  output does not already exist. No stale successful report is produced.
- `NOT_RUN`: install this checkout with the regression dependencies, bind parameters,
  reduce qubits or decompose custom gates; unsupported methods are not simulated.
- `INCOMPATIBLE`: inspect `changes`; do not widen axes simply to remove a failure.
- To share diagnostics, send verdict, failed metric names and dependency versions
  after review. Do not share full captures, factory paths or repo names by default.

Team's proposed USD 149/workspace/month is a validation price for hosted private
baseline/policy/history management. It is not on sale through these commands.

## Optional private history

The local result is complete without upload. [Previewed private summaries](private-regression-summaries.md) describe the optional transport, redaction, scoped credentials, hosted availability and independent upload status.
