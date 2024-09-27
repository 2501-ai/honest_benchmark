import os
import subprocess
import sys
import signal

COMMAND_TIMEOUT = 600  # 10 minutes

# Global variable to hold the subprocess
subprocess_instance = None


def signal_handler(sig, frame):
    print('You pressed CTRL+C! Terminating subprocess...')
    if subprocess_instance:
        subprocess_instance.terminate()
        subprocess_instance.wait()
    sys.exit(0)


# Register the signal handler for SIGINT (CTRL+C)
signal.signal(signal.SIGINT, signal_handler)


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
    global subprocess_instance
    try:
        subprocess_instance = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        stdout, stderr = subprocess_instance.communicate()
        return stdout.strip(), stderr.strip(), subprocess_instance.returncode
    except KeyboardInterrupt:
        print('Interrupted! Terminating subprocess...')
        if subprocess_instance:
            subprocess_instance.terminate()
            subprocess_instance.wait()
        sys.exit(0)
    finally:
        subprocess_instance = None
    return result.stdout.strip(), result.stderr.strip(), result.returncode
