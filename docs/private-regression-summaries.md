# Preview an optional private report upload

The local comparison is complete without an account or upload. The optional
transport below supports the private workspace API when that service is enabled
and the workspace has an active entitlement. A CLI command existing does not mean
the hosted service or live billing is available. See the workspace's actual state.

## Review the exact data first

```bash
ketqat regression preview sample/report/report.json --output summary.json
```

Open `summary.json`. It contains selected compiled resource counts, total-variation
estimate and shot budget when selected, policy thresholds, changed **field names**,
six-state verdict, CI exit code and stable hashes. It excludes Python source,
circuits, raw counts/probabilities, local paths, environment values and raw
case/repository names. Unselected metrics are redacted. Local snapshots and reports
retain full reproduction detail; keep them in your own private storage.

**Metrics and hashes can still be confidential.** Hashing is not anonymization;
a guessed case name can be matched to its hash. Choose non-sensitive local case
aliases or keep everything local if these summaries reveal too much. Review files
are created with owner-only permissions on POSIX. Do not publish them as public CI
artifacts. No third-party model receives the data.

## Upload with a scoped, expiring credential

Create a repository-specific token in an entitled private workspace. Store it as
`KETQAT_REGRESSION_TOKEN` in your local environment or protected CI secrets. Never
put a credential in a command argument, URL, committed file or Actions summary.
Copy the preview command's SHA256, then deliberately authorize those exact bytes:

```bash
ketqat regression upload summary.json \
  --repository REPOSITORY_ID_FROM_WORKSPACE \
  --confirm-sha256 SHA256_PRINTED_BY_PREVIEW
```

The file's hash must still match. The client uses HTTPS, refuses redirects, caps
the payload at 100 KiB and response at 8 KiB, and makes at most three attempts with
10-second timeouts and 2/4-second delays for temporary errors. Retries carry the
same idempotency key. `--server` explicitly selects a different HTTPS origin;
HTTP is accepted only for loopback development. Use a credential for that server.
Requests identify themselves as `KetQat-SDK regression-upload` in the User-Agent
header; they do not impersonate a browser or include environment details there.

`UPLOAD: STORED` or `DUPLICATE` means the server acknowledged the original verdict.
Upload exit 0 describes transport success; it never converts REGRESSION into a
passing comparison. Keep the comparison command's exit code as your CI gate.
An unavailable API, missing entitlement or unknown response fails the upload with
exit 4, and the local comparison remains available. In particular:

| Response | Action |
|---|---|
| 401 | Replace the expired or revoked scoped token. |
| 403 | Check repository scope and the workspace's actual subscription state. |
| 409 | Review active policy/baseline and re-run locally. Do not auto-promote. |
| 413 / 422 | Inspect the preview's size or schema; keep the local report. |
| 429 | Check the workspace usage page and reset time. |
| temporary outage | Keep the local report, retry later; no unbounded loop. |

## Keep untrusted PR code away from secrets

Run local comparisons on `pull_request` with read-only GitHub permissions and no
upload credential. Upload only in a separate job on a protected, reviewed branch,
with the secret attached to that job. Never run a fork's Python code under
`pull_request_target`, pass a long-lived PAT, or give arbitrary PR jobs the upload
token. A GitHub App is not required. Customer CI compute charges are separate.

## What the server checks

The SDK's TypeScript boundary rejects unknown fields, non-finite values,
unselected observations, invalid policies and contradictory verdict/exit codes.
It recomputes resource thresholds and simultaneous Hoeffding interval arithmetic
from the allowlisted observations. It cannot independently reconstruct private
simulation results from a redacted summary. The provenance remains
`CLIENT_REPORTED`, not scientifically verified, certified or independently
reproduced. Matching selected output distributions is not program equivalence.
