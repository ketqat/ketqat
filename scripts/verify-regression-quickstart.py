"""Build a wheel, install in a clean venv/cold uv cache, execute real Qiskit.

Uses network only for public package installation. No hosted KetQat upload.
Stores measured evidence and the intentional sample in the chosen output dir.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
root = Path(__file__).resolve().parents[1]

def run(command, **kwargs):
    return subprocess.run(command, check=True, cwd=root, **kwargs)

with tempfile.TemporaryDirectory(prefix='ketqat-regression-verify-') as tmp:
    temp = Path(tmp)
    env = dict(os.environ, UV_CACHE_DIR=str(temp/'cold-cache'))
    started = time.monotonic()
    run(['uv','venv','--python','3.11',str(temp/'venv')],env=env)
    python = temp/'venv/bin/python'
    run(['uv','pip','install','--python',str(python),'--require-hashes',
         '-r','requirements-regression-py311.txt'],env=env)
    run(['uv','pip','install','--python',str(python),'--require-hashes',
         '-r','requirements-regression-build-py311.txt'],env=env)
    run(['uv','build','--python',str(python),'--no-build-isolation','--wheel',
         '--out-dir',str(temp/'dist'),'python'],env=env)
    wheel = next((temp/'dist').glob('*.whl'))
    run(['uv','pip','install','--python',str(python),'--no-deps',str(wheel)],env=env)
    result = subprocess.run([str(temp/'venv/bin/ketqat'),'regression','sample',
                             '--output-dir',str(args.output.resolve()/'sample')],cwd=temp,env=env)
    elapsed = time.monotonic()-started
    if result.returncode != 1:
        raise RuntimeError('The intentional sample must fail CI with REGRESSION.')
    report=json.loads((args.output/'sample/report/report.json').read_text(encoding='utf-8'))
    if report['verdict'] != 'REGRESSION':
        raise RuntimeError('The sample verdict must be REGRESSION.')
    if abs(next(c for c in report['checks'] if c['metric']=='total_variation')['estimate']-0.5) >= 1e-12:
        raise RuntimeError('The sample distance must match the independent Bell reference.')
    dependencies = subprocess.run(['uv','pip','freeze','--python',str(python)],capture_output=True,text=True,check=True).stdout
    # The wheel's temporary file:// URL is local verification detail, not a
    # distributable installation claim.
    dependencies = '\n'.join(line for line in dependencies.splitlines() if not line.startswith('ketqat @'))
    evidence={'method':'clean Python 3.11 virtualenv, cold uv package cache; hashed runtime and build dependencies, source wheel build included; real Qiskit ideal simulation',
              'elapsed_seconds':round(elapsed,3),'target_seconds':600,'met_target':elapsed<=600,
              'platform':platform.platform(),'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),
              'dependencies':dependencies,'sample_exit_code':result.returncode,'verdict':report['verdict'],
              'uploads':0,'claim':'Maintainer engineering verification, not an independent customer trial.'}
    (args.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(evidence,indent=2))
