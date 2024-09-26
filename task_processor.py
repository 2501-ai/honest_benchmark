import os
import sys
import zipfile

from benchmark_report import BenchmarkReport
from utils.command import run_command


def process_task(task, files_dir, benchmark_report: BenchmarkReport, max_retries=3):
    """
    Process a single task and record the result in the benchmark report.

    Args:
        task (dict): The task dictionary.
        files_dir (str): The directory containing the files.
        benchmark_report (BenchmarkReport): Instance of BenchmarkReport to store results.
        max_retries (int): Maximum number of retries for the task.
    """
    task_id = task['id']
    input_command = task['input']
    test_command = task.get('test_command', None)
    test_script = task.get('test_script', None)

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

    retries = 0
    passed = False
    error_message = None

    while retries <= max_retries:
        try:
            if retries > 0:
                print(f"Retrying task {task_id} (attempt {retries + 1})")
            # Execute the input command
            print(f"Executing command: @2501 {input_command}")
            stdout, stderr, returncode = run_command(f"cd {files_dir}/{task_id} && @2501 {input_command}")
            print(f"Command stdout: {stdout}")
            print(f"Command stderr: {stderr}")
            print(f"Command returncode: {returncode}")

            if returncode != 0:
                print(f"Command failed with return code {returncode}")
                print(f"Error output: {stderr}")
                retries += 1
                continue

            test_local = locals()
            # Run the test command or script
            if test_command:
                print(f"Executing script at {test_command}")
                # execute the script at path, with args
                out, err, code = run_command(test_command)
                print(f"Test command stdout: {out}")
                print(f"Test command stderr: {err}")
                print(f"Test command returncode: {code}")
                test_local['output'] = code == 0 and 'PASS' or 'FAIL'
            elif test_script:
                print(f"Executing in-line test script")
                exec(test_script, globals(), test_local)

            output = test_local.get('output', 'FAIL')
            print(f"Test {task_id} output: {output}")

            passed = output.strip().upper() == "PASS"
            break

        except Exception as e:
            print(f"Test failed: {str(e)}", file=sys.stderr)
            error_message = str(e)
            retries += 1

    # Store the result in the benchmark report
    benchmark_report.add_result(task_id, input_command, test_command or test_script, passed, retries,
                                error_message=error_message)
