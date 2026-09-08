# AGENTS.md

## Mission

The current priority is a low-touch business helping small Qiskit software teams
catch regressions on PRs and SDK upgrades. The free local/CI comparison is the
core; private team baseline/policy management and history are the proposed paid
service. See [ADR 0015](https://github.com/ketqat/ketqat-planning/blob/main/docs/architecture/adr/0015-continuous-qiskit-regression-business.md).

KetQat's own software subscription and test payment integration are authorized by
the maintainer's 2026-09-08 commercial rebuild directive. Prior blanket no-billing,
no-test-checkout and roadmap-first restrictions are superseded. Record a proposed
price as a hypothesis; never invent sales, customers, costs or retention.

Keep Engineering-ready, Commercially-ready and Market-validated separate. Live
selling still requires actual seller/legal/account setup. New paid capacity and
external outreach require explicit authorization. Existing public OSS licenses,
private data, shared URLs, scientific validity and review gates are preserved.

QPU marketplace/resale, provider billing, persistent provider credentials and
unconfirmed hardware execution remain excluded. Existing research functionality
is preserved, but unfinished studies/MCP/QEC/FTQC breadth is not a prerequisite.
No customer source runs on KetQat servers; initial compute is local/customer CI.

## Repository responsibility

`ketqat-sdk` owns:

- Scientific public contracts
- Zod runtime validation and generated JSON Schemas
- Reproducibility hashing
- Scientific compatibility logic
- Typed REST client
- Public examples and demo fixtures
- Local TypeScript/Python runner support

Adjacent responsibilities:

- `ketqat-web` owns UI, APIs, Prisma/PostgreSQL, authorization, GitHub metadata import, and deployment.
- `ketqat-planning` owns vision, scope, roadmap, ADRs, RFCs, and cross-repository planning.

## Required reading before editing

1. `AGENTS.md`
2. `README.md`
3. `CONTRIBUTING.md`
4. Relevant files under `src/contracts`, `src/schemas`, `src/reproducibility`, `src/compatibility`, or `python/src`
5. `ketqat-planning/CONTEXT.md`
6. Relevant ADRs or RFCs in `ketqat-planning`

Inspect current code and tests instead of trusting stale documentation.

## Commands

- Install: `npm ci`
- Build and regenerate schemas: `npm run build`
- Test: `npm test`
- Python test setup: `python3.11 -m pip install -e "python[qec]" pytest`
- Python tests: `python3.11 -m pytest python/tests`
- Python runner smoke check: `ketqat run examples/qec/surface-code-memory.yaml --output /tmp/ketqat-qec-run.json`

## Development rules

- Create or identify a GitHub Issue before substantial implementation.
- Use a feature branch; use `chore/...`, `feature/...`, or `fix/...`.
- Link PRs to Issues.
- Run documented tests before requesting review.
- Update README, schemas, examples, or planning docs when behavior changes.
- Report unverified assumptions.

## SDK-specific rules

- Review schema backward compatibility for public contract changes.
- Add or update TypeScript tests for schema, hashing, compatibility, client, and demo data changes.
- Add Python tests for runner and cross-language hash behavior when runner behavior changes.
- Maintain cross-language reproducibility hash parity.
- Normal QEC runner execution must use real NumPy, Stim, and PyMatching dependencies; never reintroduce an automatic synthetic fallback.
- Do not add web UI, Prisma, PostgreSQL, authentication, deployment, or provider-catalog functionality.
- Do not duplicate implementation behavior that belongs in `ketqat-web`.

## Security and scientific integrity

- Do not commit secrets.
- Do not execute arbitrary uploaded code.
- Do not store provider credentials.
- Mark synthetic records with `is_demo: true`.
- Do not present demo results as scientific performance claims.
- Do not rank or compare incompatible runs.

## Cross-repository changes

Create a parent issue in `ketqat-planning` for cross-repository initiatives, then implementation issues in owning repositories. Use bidirectional links if GitHub sub-issues are unavailable.
