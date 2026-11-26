"""Run dbt explicitly: run never implies test. Each DAG run has isolated artifacts."""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from ticketing.common import DATA
from ticketing.schema import require

PROJECT = Path(os.environ.get('DBT_PROJECT_DIR', '/opt/project/dbt'))

def invoke(command, run_id='tools', stage=None, full_refresh=False, bronze_mode='full_snapshot', model=None):
    require(bool(re.fullmatch(r'[a-zA-Z0-9_-]+', run_id)), 'Unsafe run id')
    require(command in ('run','test','debug','parse','compile','docs'), 'Unsupported command')
    require(stage in (None,'silver','gold'), 'Unsupported stage')
    require(command not in ('run','test') or stage is not None, 'Select silver or gold')
    require(bronze_mode in ('full_snapshot','append_history'), 'Invalid bronze mode')
    if model is not None:
        from ticketing.model_catalog import MODEL_GROUPS
        require(stage in MODEL_GROUPS and model in MODEL_GROUPS[stage], 'Model does not belong to stage')
    folder = DATA / 'elt' / run_id / (stage or command)
    if stage:
        folder = folder / (model or '_all') / command
    folder.mkdir(parents=True, exist_ok=True)
    args = [os.environ.get('DBT_BIN','/opt/dbt/bin/dbt'), command]
    if command == 'docs':
        args += ['generate', '--static']
    args += ['--project-dir',str(PROJECT),'--profiles-dir',str(PROJECT),
             '--target-path',str(folder/'target'),'--log-path',str(folder/'logs'),
             '--vars',json.dumps({'bronze_mode':bronze_mode})]
    if stage:
        args += ['--select',model or 'tag:'+stage,'--indirect-selection','cautious']
    if full_refresh and command == 'run':
        args.append('--full-refresh')
    env = dict(os.environ, DBT_SEND_ANONYMOUS_USAGE_STATS='false', DBT_PARTIAL_PARSE='false')
    proc = subprocess.Popen(args, env=env, start_new_session=os.name != 'nt')
    try:
        code = proc.wait(timeout=3600)
    except BaseException:
        if os.name != 'nt':
            import signal
            os.killpg(proc.pid,signal.SIGKILL)
        else:
            proc.kill()
        proc.wait()
        raise
    require(code == 0, f'dbt failed; inspect {folder}')
    return str(folder)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run','test','debug','parse','compile','docs'])
    parser.add_argument('--stage', choices=['silver','gold'])
    parser.add_argument('--model', help='Run one model from the selected stage')
    parser.add_argument('--full-refresh', action='store_true')
    parser.add_argument('--bronze-mode', choices=['full_snapshot','append_history'], default='full_snapshot')
    args = parser.parse_args()
    invoke(args.command, stage=args.stage, full_refresh=args.full_refresh, bronze_mode=args.bronze_mode, model=args.model)
