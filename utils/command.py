import os
import subprocess

COMMAND_TIMEOUT = 600  # 10 minutes


def run_command(command):
    """
    Run a shell command and return the output.

    Args:
        command (str): The command to run.

    Returns:
        tuple: stdout, stderr, and return code of the command.
    """
    env = os.environ.copy()
    env['TERM'] = 'xterm'  # Set the TERM environment variable
    env['PYTHONIOENCODING'] = 'utf-8'  # Ensure Python uses UTF-8 encoding
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env, timeout=COMMAND_TIMEOUT)
    return result.stdout.strip(), result.stderr.strip(), result.returncode
