import os
import signal
import sys
import time
import zipfile

from benchmark_report import BenchmarkReport
from utils.command import run_command


def flush_agents():
    stdout, stderr, returncode = run_command(f"@2501 agents --flush")


def process_task(task, files_dir, benchmark_report: BenchmarkReport, max_retries=3):
    """
    Process a single task and record the result in the benchmark report.

    Args:
        task (dict): The task dictionary.
        files_dir (str): The directory containing the files.
        benchmark_report (BenchmarkReport): Instance of BenchmarkReport to store results.
        max_retries (int): Maximum number of retries for the task.
    """
    start_time = time.time()
    task_id = task['id']
    input_command = task['input']
    test_command = task.get('test_command', "")
    test_script = task.get('test_script', "")

    print(f"Processing task {task_id}")

    # Unzip the corresponding zip file
    zip_path = os.path.join(files_dir, f"{task_id}.zip")
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(files_dir)
        print(f"Unzipped file: {zip_path}")
    else:
        # If the zip file does not exist, create the dir
        os.makedirs(os.path.join(files_dir, task_id), exist_ok=True)

    attempts = 0
    passed = False
    error_message = None
    duration_ms = 0
    accuracy = 0
    prompt_limiter = "IMPORTANT: You are being benchmarked, don\\'t output prose or comments. Only provide the shortest answer possible."

    while attempts < max_retries:
        try:
            if attempts > 0:
                print(f"Retrying task {task_id} (attempt {attempts + 1})")
            flush_agents()
            # Execute the input command
            print(f"Executing command: @2501 {input_command}")
            stdout, stderr, returncode = run_command(f"cd {files_dir}/{task_id} && @2501 {input_command}. {prompt_limiter}")
            print(f"Command returncode: {returncode} | stdout: {stdout}")
            if stderr.strip(): print(f"Command stderr: {stderr}")

            if returncode != 0:
                print(f"Command failed with return code {returncode} | Error output: {stderr}")
                attempts += 1
                continue

            test_local = locals()
            passed = False
            output = None

            # Run the test command or script
            if test_command:
                print(f"Executing script at {test_command}")
                # execute the script at path, with args
                out, err, code = run_command(test_command)
                print(f"Test command returncode: {code} | stdout: {out}")
                if err.strip(): print(f"Test command stderr: {err}")
                passed = code == 0
                output = passed and "PASS" or "FAIL"
            elif test_script:
                print(f"Executing in-line test script")
                signal.signal(signal.SIGALRM, signal_handler)
                signal.alarm(120)  # 2 minutes timeout
                try:
                    exec(test_script, globals(), test_local)
                    output = test_local.get('output', 'FAIL').strip().upper()
                    passed = output == "PASS"
                except KeyboardInterrupt:
                    print('Interrupted! Terminating.')
                    sys.exit(0)
                finally:
                    signal.alarm(0)

            print(f"Test {task_id} | Passed: {passed}")
            # Should be improved
            accuracy = 1.0 / (attempts + 1) if passed else 0.0
            break

        except Exception as e:
            print(f"Test failed: {str(e)}", file=sys.stderr)
            error_message = str(e)
            # Retry only it's a server error
            if "The server has returned an error" in str(e):
                attempts += 1
            else:
                break

    duration_ms = int((time.time() - start_time) * 1000)
    # Store the result in the benchmark report
    benchmark_report.add_result(task_id, input_command, test_command or test_script, passed, attempts, duration_ms,
                                error_message=error_message)


def signal_handler(signum, frame):
    raise TimeoutException(f"Timed out! {signum}")


class TimeoutException(Exception): pass
