# ketqat

Catch quantum regressions before you merge. For the Qiskit 2.x local/CI flow, start with the [regression quickstart](https://github.com/ketqat/ketqat-sdk/blob/feature/commercial-regression/docs/regression-quickstart.md). No account or upload is required. Public PyPI publication remains pending.


Local benchmark runner for [KetQat](https://ketqat.com) — a vendor-neutral registry for reproducible quantum error-correction and quantum-algorithm experiments.

```bash
pip install "ketqat[qec]"
ketqat run examples/qec/surface-code-memory.yaml --output run.json
```

`ketqat run` executes a benchmark manifest against real dependencies (Stim, PyMatching for QEC; NumPy for algorithms), producing a result JSON with a canonical reproducibility hash. No synthetic fallback is used for QEC experiments — install the `qec` extra to run them.

## Extras

- `pip install "ketqat[qec]"` — Stim + PyMatching for QEC decoder/code benchmarks.
- `pip install "ketqat[algorithms]"` — NumPy for quantum-algorithm benchmarks.
- `pip install "ketqat[all]"` — both.

## Submitting a result

```bash
curl -X POST https://ketqat.com/api/runs/import \
  -H "Authorization: Bearer kq_..." \
  -H "content-type: application/json" \
  -d @run.json
```

Create an API token at [ketqat.com/settings](https://ketqat.com/settings) after signing in. See the [ketqat-sdk](https://github.com/ketqat/ketqat-sdk) repository for the manifest format, schemas, and the TypeScript client.

Source, contracts, and examples: <https://github.com/ketqat/ketqat-sdk>. Apache-2.0.
