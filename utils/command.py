import os
import subprocess
import sys
import signal

COMMAND_TIMEOUT = 600  # 10 minutes

# Global variable to hold the subprocess
subprocess_instance = None


def signal_handler(sig, frame):
    print("You pressed CTRL+C! Terminating subprocess...")
    if subprocess_instance:
        subprocess_instance.terminate()
        subprocess_instance.wait()
    sys.exit(0)


# Register the signal handler for SIGINT (CTRL+C)
signal.signal(signal.SIGINT, signal_handler)


def run_command(command, input_data=None):
    """
    Run a shell command and return the output.

    Args:
        command (str): The command to run.
        input_data (str, optional): Input data to pass to the command as stdin.

    Returns:
        tuple: stdout, stderr, and return code of the command.
    """
    env = os.environ.copy()
    env["TERM"] = "xterm"  # Set the TERM environment variable
    env["PYTHONIOENCODING"] = "utf-8"  # Ensure Python uses UTF-8 encoding
    global subprocess_instance
    try:
        subprocess_instance = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            env=env,
        )
        stdout, stderr = subprocess_instance.communicate(input=input_data)
        return stdout.strip(), stderr.strip(), subprocess_instance.returncode
    except KeyboardInterrupt:
        print("Interrupted! Terminating subprocess...")
        if subprocess_instance:
            subprocess_instance.terminate()
            subprocess_instance.wait()
        sys.exit(0)
    finally:
        subprocess_instance = None
