import json
import os
import sys
import subprocess
import zipfile
import argparse

COMMAND_TIMEOUT = 600 # 10 minutes

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


def write_result(task, passed, result_jsonl_path):
    """
    Write the result to the result JSONL file.

    Args:
        task (dict): The task dictionary.
        passed (bool): Whether the task passed or not.
        result_jsonl_path (str): Path to the result JSONL file.
    """
    task['passed'] = passed
    with open(result_jsonl_path, 'a') as result_file:
        result_file.write(json.dumps(task) + '\n')


def remove_previous_folders(files_dir):
    """
    Remove all previous folders in the files directory.

    Args:
        files_dir (str): The directory containing the files.
    """
    run_command(f"find {files_dir}/* -type d -exec rm -rf {{}} +")


def process_task(task, files_dir, result_jsonl_path):
    """
    Process a single task.

    Args:
        task (dict): The task dictionary.
        files_dir (str): The directory containing the files.
        result_jsonl_path (str): Path to the result JSONL file.
    """
    task_id = task['id']
    input_command = task['input']
    test_command = task['test']

    print(f"Processing task {task_id}")

    # Unzip the corresponding zip file
    zip_path = os.path.join(files_dir, f"{task_id}.zip")
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(files_dir)
        print(f"Unzipped file: {zip_path}")
    else:
        # Create the directory for the missing zip file
        os.makedirs(f"{files_dir}/{task_id}", exist_ok=True)
        print(f"Directory created: {files_dir}/{task_id}")

    # Flush the agents
    flush_stdout, flush_stderr, flush_returncode = run_command(f"cd {files_dir}/{task_id} && @2501 agents --flush")
    if flush_returncode != 0:
        print(f"Error flushing agents: {flush_stderr}")
        write_result(task, False, result_jsonl_path)
        return

    # Execute the @2501 command
    print(f"Executing command: @2501 {input_command}")
    stdout, stderr, returncode = run_command(f"cd {files_dir}/{task_id} && @2501 {input_command}")
    print(f"Command stdout: {stdout}")
    print(f"Command stderr: {stderr}")
    print(f"Command returncode: {returncode}")

    if returncode != 0:
        print(f"Command failed with return code {returncode}")
        print(f"Error output:{stderr}")
        write_result(task, False, result_jsonl_path)
        return

    # Run the test command
    print(f"Running test: {test_command}")
    try:
        test_locals = {}
        exec(test_command, globals(), test_locals)
        output = test_locals['output']
        print(f"Test {task_id} output: {output}")

        passed = output.strip().upper() == "PASS"
        write_result(task, passed, result_jsonl_path)
    except Exception as e:
        print(f"Test failed: {str(e)}", file=sys.stderr)
        task['error'] = str(e)
        write_result(task, False, result_jsonl_path)


def main(jsonl_path, testnum, testfrom):
    """
    Main function to process tasks from a JSONL file.

    Args:
        jsonl_path (str): Path to the JSONL file containing the tasks.
        testnum (str): Specific test ID to run.
        testfrom (str): Test ID to start running from.
    """
    files_dir = 'files'
    remove_previous_folders(files_dir)
    result_jsonl_path = f'{jsonl_path}_result.jsonl'

    os.makedirs(files_dir, exist_ok=True)

    is_test_from = False
    with open(jsonl_path, 'r') as file:
        for line in file:
            if testnum and json.loads(line)['id'] != testnum:
                continue
            if testfrom and not is_test_from:
                if json.loads(line)['id'] == testfrom:
                    is_test_from = True
                else:
                    continue

            try:
                task = json.loads(line)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in line: {line}")
                continue
            except KeyError as e:
                print(f"Error: Missing key in task: {e}")
                continue

            process_task(task, files_dir, result_jsonl_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate tasks from a JSONL file.')
    parser.add_argument('problem_file', type=str, help='Path to the JSONL file containing the tasks.', nargs='?',
                        default='honest_benchmark.jsonl')
    parser.add_argument('--test', type=str, help='Test ID to run.', default=None, dest='testnum')
    parser.add_argument('--from', type=str, help='Test ID to run from.', default=None, dest='testfrom')
    args = parser.parse_args()
    print("args", args)
    main(args.problem_file, args.testnum, args.testfrom)
