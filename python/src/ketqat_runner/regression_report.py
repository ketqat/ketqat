"""Portable offline report. Escape all data; no scripts, trackers or remote assets."""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def markdown(report: dict[str, Any]) -> str:
    def escape(value):
        value = html.escape(str(value), quote=True).replace('\r', ' ').replace('\n', ' ')
        return ''.join('\\' + char if char in '\\`*_{}[]()#+-.!|>' else char for char in value)
    verdict = report['verdict']
    if verdict not in ('WITHIN_POLICY', 'REGRESSION', 'INCONCLUSIVE', 'INCOMPATIBLE', 'ERROR', 'NOT_RUN'):
        raise ValueError('Invalid report verdict.')
    lines = [f"## KetQat: {verdict}", '', f"Case: {escape(report['case_id'])}", '',
             escape(report['conclusion']), '', '| Check | Verdict | Evidence |', '| --- | --- | --- |']
    for check in report['checks']:
        evidence = json.dumps({k: v for k, v in check.items() if k not in ('metric', 'verdict')}, sort_keys=True)
        lines.append(f"| {escape(check['metric'])} | {escape(check['verdict'])} | {escape(evidence)} |")
    lines += ['', 'Next: ' + ' '.join(escape(step) for step in report['next_steps']), '', escape(report['scope']), '',
              'Upload: NOT_REQUESTED. This report remains local unless you explicitly share it.', '']
    return '\n'.join(lines)


def html_report(report: dict[str, Any], baseline: dict, candidate: dict) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    def check_card(check):
        label = {'two_qubit_gates': 'Two-qubit gates', 'total_variation': 'Output distribution',
                 'size': 'Compiled gates', 'depth': 'Circuit depth'}.get(check['metric'], check['metric'])
        if 'reason' in check:
            evidence = check['reason']
        elif check['metric'] == 'total_variation':
            evidence = f"Distance {check['estimate']:.6g} · allowed up to {check['maximum']:.6g}."
            if check.get('family_alpha') is not None:
                evidence += f" Simultaneous interval: [{check['lower']:.6g}, {check['upper']:.6g}]."
        else:
            evidence = f"Baseline {check['baseline']} → candidate {check['candidate']}. Maximum allowed: {check['maximum']:.6g}."
        return f"<article class='check'><div class='check-title'><h3>{esc(label)}</h3><span class='tag'>{esc(check['verdict'])}</span></div><p>{esc(evidence)}</p></article>"
    checks = ''.join(check_card(c) for c in report['checks'])
    details = esc(json.dumps({'report': report, 'baseline': baseline, 'candidate': candidate}, indent=2, allow_nan=False))
    sample = f"<p class='note'>{esc(report['sample'])}</p>" if report.get('sample') else ''
    steps = ''.join(f'<li>{esc(step)}</li>' for step in report['next_steps'])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>{esc(report['verdict'])} · KetQat · {esc(report['case_id'])}</title>
<style>:root{{color-scheme:light dark;font-family:system-ui,sans-serif;line-height:1.6}}body{{margin:auto;max-width:1000px;padding:24px}}
h1{{font-size:clamp(1.7rem,4vw,2.6rem);line-height:1.15}}header{{border-bottom:2px solid #888;padding-bottom:20px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.8rem}}
.check{{border:1px solid #888;border-radius:8px;padding:16px;margin:12px 0}}.check-title{{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center}}h3{{font-size:1rem;margin:0}}.check p{{margin:12px 0 0}}
summary{{cursor:pointer;padding:16px 0;font-weight:600}}.tag{{font-family:monospace;font-weight:bold}}.note{{border-left:3px solid #888;padding-left:16px}}
@media(max-width:600px){{body{{padding:16px}}.tag{{font-size:.875rem}}}}</style></head>
<body><header><p>KetQat / Change report</p><p class="tag">{esc(report['verdict'])} · CI exit {report['exit_code']}</p>
<h1>{esc(report['conclusion'])}</h1><p>Case: {esc(report['case_id'])}</p>{sample}</header>
<main><h2>Impact and evidence</h2>{checks}
<h2>Next check</h2><ul>{steps}</ul><p class="note">{esc(report['scope'])}</p>
<h2>What changed</h2><pre>{esc(json.dumps(report['changes'], indent=2))}</pre>
<details><summary>Conditions, inputs and reproducibility details</summary><p>Re-run the recorded factory from the baseline and candidate commits with the listed dependency versions and conditions. The JSON snapshots include local circuit instructions. A hash identifies these records; it is not independent verification.</p><pre>{details}</pre></details>
<p>Data location: local. No source, circuit, measurements or identifiers were uploaded. Sharing this HTML shares the embedded inputs; inspect them first.</p>
</main></body></html>'''


def write_reports(directory: Path, report: dict, baseline: dict, candidate: dict) -> None:
    # A fresh directory prevents stale success reports surviving a failed rerun.
    directory.mkdir(parents=True, exist_ok=False)
    directory.joinpath('report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    directory.joinpath('report.html').write_text(html_report(report, baseline, candidate), encoding='utf-8')
    directory.joinpath('summary.md').write_text(markdown(report), encoding='utf-8')
