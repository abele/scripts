import os
import datetime
import builtins
import subprocess

import xonsh

#: Motivating quote to get you working
GREETING = """ (╯°□°）╯︵ ┻━┻ Let\'s do some fun!!!
[Batch, Chunk, Protect, Break]
"""
#: Exception to test if branch gets executed
hell = Exception('(╯°□°）╯︵ ┻━┻!')

cwd_base = builtins.__xonsh_env__['FORMATTER_DICT']['cwd_base']
PROJECT_MARKER = set(('.git', 'Makefile', '.ropeproject'))


def source_envdir(args, stdin=None):
    """Read envdir in current environment."""
    for root, _, file_list in os.walk(first(args, 'env')):
        for var_name in file_list:
            var_value = open(os.path.join(root, var_name)).read().rstrip()
            print(var_name)
            builtins.__xonsh_env__[var_name] = var_value


def dev(args, stdin=None):
    session_name = first(args, cwd_base())
    if session_name in _run_cmd('tmux ls; exit 0'):
        _run_cmd('tmux attach -t ' + session_name)
    else:
        _run_cmd('tmux new -s ' + session_name)


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
    venv_bin_path = os.path.join(venv_path, 'bin')

    if not os.path.exists(venv_path):
        raise OSError('Faild to activate venv: no such venv{}'.format(venv_path))

    if  'VIRTUAL_ENV' in builtins.__xonsh_env__:
        deactivate(None, None)

    path_orig = list(builtins.__xonsh_env__['PATH'])
    prompt_orig = builtins.__xonsh_env__['PROMPT']

    builtins.__xonsh_env__['VIRTUAL_ENV'] = venv_path
    builtins.__xonsh_env__['PROMPT'] = '({}) {}'.format(venv_name, prompt_orig)
    builtins.__xonsh_env__['PATH'] = [venv_bin_path]  + path_orig

    workon._path_orig = path_orig
    workon._prompt_orig = prompt_orig


def deactivate(args, stdin=None):
    """Deactivate Python virtualenv."""
    try:
        del builtins.__xonsh_env__['VIRTUAL_ENV']
        builtins.__xonsh_env__['PATH'] = workon._path_orig
        builtins.__xonsh_env__['PROMPT'] = workon._prompt_orig
    except KeyError:
        pass


def cd_base():
    """Return project root path."""
    while PROJECT_MARKER.isdisjoint(set(os.listdir())):
        xonsh.dirstack.cd([os.pardir])

    print(os.getcwd())


def _envfile(args, stdin=None):
    for line in open(first(args, '.env')):
        if line.strip() and not line.startswith('#'):
            key, value = line.split('=', 1)
            builtins.__xonsh_env__[key.strip()] = value.strip()


def setup():
    """Setup aliases."""
    builtins.aliases['dev'] = dev
    builtins.aliases['senv'] = source_envdir
    builtins.aliases['scratch'] = scratch
    builtins.aliases['workon'] = workon
    builtins.aliases['work'] = workon
    builtins.aliases['deactivate'] = deactivate
    builtins.aliases['cdb'] = cd_base
    builtins.aliases['envfile'] = _envfile


def _run_cmd(cmd):
    return subprocess.check_output(
        cmd,
        universal_newlines=True,
        stderr=subprocess.STDOUT,
        shell=True,
    )


def first(iterable, default=None):
    return next(iter(iterable or []), default)
