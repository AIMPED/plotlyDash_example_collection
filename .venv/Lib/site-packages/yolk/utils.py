"""Miscellaneous functions.

run_command borrowed from Cheesecake - See CREDITS.

"""

import os
import signal
import subprocess
import time


def get_yolk_dir():
    """Return location we store config files and data."""
    return os.path.abspath('%s/.yolk' % os.path.expanduser('~'))


def run_command(args, env=None, max_timeout=None):
    r"""Run command and return its return status code and its output.

    >>> run_command(['true'])
    (0, '')

    >>> run_command(['false'])
    (1, '')

    >>> run_command(['echo', 'hello world'])
    (0, 'hello world\n')

    """
    try:
        pipe = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                env=env)
    except Exception as errmsg:
        return 1, errmsg

    # Wait only max_timeout seconds.
    if max_timeout:
        start = time.time()
        while pipe.poll() is None:
            time.sleep(0.1)
            if time.time() - start > max_timeout:
                os.kill(pipe.pid, signal.SIGINT)
                pipe.wait()
                return 1, 'Time exceeded'

    pipe.wait()
    return pipe.returncode, pipe.communicate()[0].decode()


def command_successful(args):
    """Return True if command exited normally, False otherwise."""
    return_code, _ = run_command(args)
    return return_code == 0
