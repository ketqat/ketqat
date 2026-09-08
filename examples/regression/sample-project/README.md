# A two-qubit regression exercise

This directory is a small project you can copy into an existing test repository.
It is part of the Apache-2.0 KetQat SDK, not a new package or a claim of a customer
incident. Install the SDK with the [source quickstart](../../../docs/regression-quickstart.md).

From this directory, capture `tests/circuits.py:prepare_state` as your baseline:

```bash
ketqat regression capture tests/circuits.py:prepare_state --case-id prepare-state --output local-evidence/baseline.json
ketqat regression capture tests/circuits.py:prepare_state --case-id prepare-state --output local-evidence/unchanged.json
ketqat regression compare local-evidence/baseline.json local-evidence/unchanged.json --policy policy.json --output-dir local-evidence/unchanged-report
```

Expected: `WITHIN_POLICY`, exit 0. Now remove `circuit.cx(0, 1)` from the factory,
capture to `local-evidence/changed.json` and compare to the same baseline using a
new report directory. Expected: `REGRESSION`, exit 1, total variation near 0.5
against the 0.05 tolerance. Open that report's HTML. Changing an output directory
does not update the baseline; existing captures are never overwritten.

## Use the same exercise on a pull request

1. Copy this directory's `tests/circuits.py` and `policy.json` into a repository
   you control. Review and merge them into its protected base branch first.
2. Copy [github-actions.yml](../github-actions.yml) into
   `.github/workflows/quantum-regression.yml` in that repository. Review the
   immutable SDK and Action pins. The installation uses hashed runtime/build
   requirements; no unpublished package or missing requirements file is assumed.
3. Open a PR removing the CX gate. The job checks out the base and candidate,
   captures both on the same runner/environment and compares using the **base
   branch's policy**. The Actions step summary should report REGRESSION and fail
   the gate. An unchanged factory should pass.

The initial files must already exist at the PR base revision; adding them for
the first time cannot retrospectively create an approved baseline. This example
uses the reviewed PR base as its baseline source. It does not fetch or promote
a Team workspace baseline. If your workflow requires a particular previously
approved capture, retain that immutable capture and match all fixed conditions.

Do not copy a macOS snapshot into a Linux job and expect equal environments.
The example remeasures both sources in the same environment. For an SDK upgrade,
use separate pinned SDK environments with only the declared `qiskit` axis
changed; this circuit-change workflow intentionally pins one Qiskit version.
Add your own dependency installation only after reviewing its lock and ensuring
both captures share the fixed conditions. No QPU, account or upload is needed.

Protect the workflow, policy and baseline source with required reviews. A PR
author who can alter the test or gate itself can weaken it; this is ordinary CI,
not proof that arbitrary candidate code is safe. Fork code receives no upload
token or persisted checkout credential, and the workflow never uses
`pull_request_target`. GitHub's read token is used by checkout, not stored in
the checkouts. Do not store private captures in public artifacts or commit them.
