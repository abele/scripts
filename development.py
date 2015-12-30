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

    if name in _run_cmd('tmux ls; exit 0'):
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


def workon(args, stdin=None):
    """Activate Python virtualenv."""
    venv_name = first(args, 'venv')
    venv_path = os.path.join(os.getcwd(), venv_name)

    if not os.path.exists(venv_path):
        raise OSError('Faild to activate venv: no such venv{}'.format(venv_path))

    env = builtins.__xonsh_env__

    if  'VIRTUAL_ENV' in env:
        deactivate(None, None)

    path_orig = list(env['PATH'])
    prompt_orig = env['PROMPT']

    env['VIRTUAL_ENV'] = venv_path
    env['PROMPT'] = '({}) {}'.format(venv_name, prompt_orig)
    env['PATH'] = [os.path.join(venv_path, 'bin')]  + path_orig

    workon._path_orig = path_orig
    workon._prompt_orig = prompt_orig


def deactivate(args, stdin=None):
    """Deactivate Python virtualenv."""
    env = builtins.__xonsh_env__
    try:
        del env['VIRTUAL_ENV']
        env['PATH'] = workon._path_orig
        env['PROMPT'] = workon._prompt_orig
    except KeyError:
        raise OSError('Failed to deactivate virtualenv.')


def setup():
    """Setup aliases."""
    builtins.aliases['dev'] = dev
    builtins.aliases['senv'] = source_envdir
    builtins.aliases['scratch'] = scratch
    builtins.aliases['workon'] = workon
    builtins.aliases['work'] = workon
    builtins.aliases['deactivate'] = deactivate


def _run_cmd(cmd):
    return subprocess.check_output(
        cmd,
        universal_newlines=True,
        stderr=subprocess.STDOUT,
        shell=True,
    )


def first(iterable, default=None):
    return next(iter(iterable or []), default)
