"""Control the existing A6000 Harbor batch; credentials remain in SSH/memfd."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
from urllib.request import urlopen


REMOTE = r'''
import json, os, shutil, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
payload = json.load(sys.stdin)
root = Path('/home/syy/路由')
os.chdir(root)
fd = os.memfd_create('modelrouter-credentials', 0)
os.write(fd, json.dumps(payload.pop('credentials')).encode())
os.fchmod(fd, 0o600)
env = dict(os.environ, EXTERNAL_TEXT_MODEL_CONFIG=f'/proc/{os.getpid()}/fd/{fd}',
           PYTHONPATH=str(root / 'our-project/code/src'),
           DOCKER_HOST='unix:///home/syy/路由/.runtime/docker-vm/docker.sock',
           LITELLM_LOCAL_MODEL_COST_MAP='true', HF_HUB_OFFLINE='1',
           OMP_NUM_THREADS='40', HTTP_PROXY='http://127.0.0.1:17898',
           HTTPS_PROXY='http://127.0.0.1:17898', NO_PROXY='localhost,127.0.0.1')
os.environ.update(env)
from modelrouter.benchmark.rq1_batch import prepare
status = 0
for index, config_path in enumerate(payload['configs']):
    result, config = prepare(root / config_path, payload['revision'])
    (result / '.private').mkdir(parents=True, exist_ok=True)
    command = [str(root / '.runtime/benchmark-venv/bin/python'), '-m',
               'modelrouter.benchmark', 'rq1', config_path,
               '--source-revision', config['source_revision']]
    export = Path(tempfile.mkdtemp(prefix='rq1-watch-export.', dir=root / '.runtime'))
    def observe(pid):
        return subprocess.Popen(command + ['--watch-pids', str(pid), '--watch-interval',
                                '1200', '--export-dir', str(export)], env=env)
    if index == 0 and payload['attach_pid']:
        print(json.dumps({'attached_controller_pid': payload['attach_pid'],
                          'run_id': config['run_id'], 'export_dir': str(export)}), flush=True)
        observe(payload['attach_pid']).wait()
    if index == 0 and payload['recover_infrastructure']:
        command.append('--recover-infrastructure')
    if not (index == 0 and payload['attach_pid']) or payload['recover_infrastructure']:
        (result / 'metrics').mkdir(exist_ok=True)
        if not (result / 'metrics/resource_observations.json').exists():
            (result / 'metrics/resource_observations.json').write_text(json.dumps({
                'sampled_at': datetime.now(timezone.utc).isoformat(),
                'gpu': subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,utilization.gpu', '--format=csv'], text=True),
                'memory': subprocess.check_output(['free', '-b'], text=True),
                'resources': config['resources']}))
        with (result / '.private/controller.log').open('a') as output:
            runner = subprocess.Popen(command, env=env, stdout=output, stderr=subprocess.STDOUT)
            print(json.dumps({'run_id': config['run_id'], 'controller_pid': runner.pid,
                              'credential_holder_pid': os.getpid(), 'watch_interval_sec': 1200,
                              'export_dir': str(export)}), flush=True)
            observer = observe(runner.pid)
            status = runner.wait()
            output.write(json.dumps({'controller_pid': runner.pid, 'exit_code': status}) + '\n')
            observer.wait()
    shutil.rmtree(export)
    if status:
        break
os.close(fd)
sys.exit(status)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('configs', nargs='+', help='Existing batch JSON files, executed in order')
    parser.add_argument('--attach-pid', type=int, help='Observe the first existing batch before continuing')
    parser.add_argument('--recover-infrastructure', action='store_true', help='Run the existing one-time recovery for the first batch')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    credentials = json.loads((Path.home() / '.agent-global/外部文本模型.local.json').read_text())
    with urlopen('http://127.0.0.1:19097/configs', timeout=5) as response:
        proxy_port = json.load(response)['mixed-port']
    command = ['ssh', '-i', str(Path.home() / '.ssh/id_ed25519_remote_server'),
               '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
               '-o', 'ExitOnForwardFailure=yes', '-o', 'ServerAliveInterval=30',
               '-o', 'ServerAliveCountMax=10', '-R', f'127.0.0.1:17898:127.0.0.1:{proxy_port}',
               'syy@10.16.15.202', '/home/syy/路由/.runtime/benchmark-venv/bin/python -c ' + shlex.quote(REMOTE)]
    result = subprocess.run(command, input=json.dumps({'configs': args.configs,
                            'attach_pid': args.attach_pid,
                            'recover_infrastructure': args.recover_infrastructure,
                            'revision': revision, 'credentials': credentials}), text=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
