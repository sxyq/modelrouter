"""Control the existing A6000 Harbor batch; credentials remain in SSH/memfd."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess


REMOTE = r'''
import json, os, shutil, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
payload = json.load(sys.stdin)
root = Path('/home/syy/路由')
os.chdir(root)
config = json.loads((root / payload['config']).read_text())
result = root / config['result_dir']
(result / '.private').mkdir(parents=True, exist_ok=True)
fd = os.memfd_create('modelrouter-credentials', 0)
os.write(fd, json.dumps(payload.pop('credentials')).encode())
os.fchmod(fd, 0o600)
env = dict(os.environ, EXTERNAL_TEXT_MODEL_CONFIG=f'/proc/{os.getpid()}/fd/{fd}',
           PYTHONPATH=str(root / 'our-project/code/src'),
           DOCKER_HOST='unix:///home/syy/路由/.runtime/docker-vm/docker.sock',
           LITELLM_LOCAL_MODEL_COST_MAP='true', HF_HUB_OFFLINE='1',
           OMP_NUM_THREADS='40', HTTP_PROXY='http://127.0.0.1:17898',
           HTTPS_PROXY='http://127.0.0.1:17898', NO_PROXY='localhost,127.0.0.1')
command = [str(root / '.runtime/benchmark-venv/bin/python'), '-m',
           'modelrouter.benchmark', 'rq1', payload['config'],
           '--source-revision', payload['revision']]
os.environ.update(env)
from modelrouter.benchmark.rq1_batch import prepare
prepare(root / payload['config'], payload['revision'])
(result / 'metrics').mkdir(exist_ok=True)
(result / 'metrics/resource_observations.json').write_text(json.dumps({
    'sampled_at': datetime.now(timezone.utc).isoformat(),
    'gpu': subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu', '--format=csv'], text=True),
    'memory': subprocess.check_output(['free', '-b'], text=True),
    'resources': config['resources']}))
export = Path(tempfile.mkdtemp(prefix='rq1-watch-export.', dir=root / '.runtime'))
with (result / '.private/controller.log').open('a') as output:
    runner = subprocess.Popen(command, env=env, stdout=output, stderr=subprocess.STDOUT)
    print(json.dumps({'run_id': config['run_id'], 'controller_pid': runner.pid,
                      'credential_holder_pid': os.getpid(), 'watch_interval_sec': 1200}), flush=True)
    observer = subprocess.Popen(command + ['--watch-pids', str(runner.pid),
                               '--watch-interval', '1200', '--export-dir', str(export)], env=env)
    status = runner.wait()
    (result / '.private/controller_finished.json').write_text(json.dumps({'exit_code': status}))
    observer.wait()
shutil.rmtree(export)
os.close(fd)
sys.exit(status)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Existing batch JSON, relative to project root')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    credentials = json.loads((Path.home() / '.agent-global/外部文本模型.local.json').read_text())
    command = ['ssh', '-i', str(Path.home() / '.ssh/id_ed25519_remote_server'),
               '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
               '-o', 'ExitOnForwardFailure=yes', '-o', 'ServerAliveInterval=30',
               '-o', 'ServerAliveCountMax=10', '-R', '127.0.0.1:17898:127.0.0.1:7897',
               'syy@10.16.15.202', '/home/syy/路由/.runtime/benchmark-venv/bin/python -c ' + shlex.quote(REMOTE)]
    result = subprocess.run(command, input=json.dumps({'config': args.config,
                            'revision': revision, 'credentials': credentials}), text=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
