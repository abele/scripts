import os
import datetime
import builtins
import subprocess

import xonsh

#: Motivating quote to get you working
GREETING = '（╯°□°）╯︵(\ .o.)\ GET SHREDING!!!'
#: Exception to test if branch gets executed
hell = Exception('(╯°□°）╯︵ ┻━┻!')


def source_envdir(args, stdin=None):
    """Read envdir in current environment."""
    env = builtins.__xonsh_env__
    path = next(iter(args or []), 'env')

    for root, _, file_list in os.walk(path):
        for env_file in file_list:
            print(env_file)
            env[env_file] = open(os.path.join(root, env_file)).read().rstrip()


def dev(args, stdin=None):
    env = builtins.__xonsh_env__
    name = next(iter(args or []), env['FORMATTER_DICT']['cwd_base']())

    if name in _run_cmd('tmux ls'):
        _run_cmd('tmux attach -t ' + name)
    else:
        _run_cmd('tmux new -s ' + name)


def scratch(args, stdin=None):
    """Create new scratch directory."""
    home_dir = os.path.expanduser('~')
    timestamp_str = str(int(datetime.datetime.now().timestamp()))
    new_dir = os.path.join(home_dir, 'Tmp', 'scratch-' + timestamp_str)
    scratch_dir = os.path.join(home_dir, 'scratch')

    os.mkdir(new_dir)
    os.remove(scratch_dir)
    os.symlink(new_dir, scratch_dir)

    xonsh.dirstack.cd([scratch_dir])
    print('New \'{}\' dir ready for grinding (⌐■_■)'.format(new_dir))

_ORIG_PATH = None
_ORIG_PROMPT = None

def workon(args, stdin=None):
    """Activate Python virtualenv."""
    env = builtins.__xonsh_env__
    if args:
        venv_name = args[0]
    else:
        venv_name = 'venv'

    _ORIG_PATH = list(env['PATH'])
    _ORIG_PROMPT = env['PROMPT']
    venv_path = os.path.join(os.getcwd(), venv_name)

    if not os.path.exists(venv_path):
        raise OSError('No such virtualenv: %s' % venv_path)

    env['PATH'] = [os.path.join(venv_path, 'bin')]  + _ORIG_PATH
    env['VIRTUAL_ENV'] = venv_path
    env['PROMPT'] = '({}) {}'.format(venv_name, _ORIG_PROMPT)


def deactivate(args, stdin=None):
    """Deactivate Python virtualenv."""
    env = builtins.__xonsh_env__
    del env['VIRTUAL_ENV']
    env['PATH'] = list(_ORIG_PATH)
    env['PROMPT'] = _ORIG_PROMPT


def z(args, stdin=None):
    _fasd_ret = _run_cmd('fasd -d ' + args[0])
    _fasd_ret = _fasd_ret.splitlines()[0]
    xonsh.dirstack.cd([_fasd_ret])


def setup():
    """Setup aliases."""
    builtins.aliases['dev'] = dev
    builtins.aliases['senv'] = source_envdir
    builtins.aliases['scratch'] = scratch
    builtins.aliases['workon'] = workon
    builtins.aliases['work'] = workon
    builtins.aliases['deactivate'] = deactivate
    builtins.aliases['z'] = z


def _run_cmd(cmd):
    return subprocess.check_output(
        cmd,
        universal_newlines=True,
        stderr=subprocess.STDOUT,
        shell=True,
    )
