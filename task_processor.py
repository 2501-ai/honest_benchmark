import os
import zipfile

from utils.command import run_command
from utils.result import write_result


def process_task(task, files_dir, result_jsonl_path, max_retries=3):
    """
    Process a single task.

    Args:
        task (dict): The task dictionary.
        files_dir (str): The directory containing the files.
        result_jsonl_path (str): Path to the result JSONL file.
        max_retries (int): Maximum number of retries for the task.
    """
    task_id = task['id']
    input_command = task['input']

    if 'script_path' in task:
        test_command = f"python3 {task['script_path']}"
    elif 'test_script' in task:
        test_command = task['test_script']
    else:
        raise ValueError("No test script specified in the task.")

    print(f"Processing task {task_id}")

    # Unzip the corresponding zip file
    zip_path = os.path.join(files_dir, f"{task_id}.zip")
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(files_dir)
        print(f"Unzipped file: {zip_path}")
    else:
        os.makedirs(f"{files_dir}/{task_id}", exist_ok=True)
        print(f"Directory created: {files_dir}/{task_id}")

    retries = 0
    while retries <= max_retries:
        try:
            # Flush the agents
            flush_stdout, flush_stderr, flush_returncode = run_command(
                f"cd {files_dir}/{task_id} && @2501 agents --flush")
            if flush_returncode != 0:
                print(f"Error flushing agents: {flush_stderr}")
                retries += 1
                continue

            # Execute the @2501 command
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

            # Run the test command
            print(f"Running test: {test_command}")
            try:
                test_locals = {}
                exec(test_command, globals(), test_locals)
                output = test_locals['output']
                print(f"Test {task_id} output: {output}")

                passed = output.strip().upper() == "PASS"
                write_result(task, passed, result_jsonl_path, retries=retries)
                return

            except Exception as e:
                print(f"Test failed: {str(e)}")
                write_result(task, False, result_jsonl_path, error_message=str(e), retries=retries)
                retries += 1

        except Exception as e:
            print(f"Processing failed: {str(e)}")
            write_result(task, False, result_jsonl_path, error_message=str(e), retries=retries)
            retries += 1

    # Final result after max retries
    if retries > max_retries:
        write_result(task, False, result_jsonl_path, error_message="Max retries exceeded", retries=max_retries)
