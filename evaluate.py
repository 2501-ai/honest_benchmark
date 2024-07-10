import json
import os
import subprocess
import zipfile
import sys

# Define the path to the JSONL file and the files directory
jsonl_path = 'honest_benchmark.jsonl'
files_dir = 'files'

def run_command(command):
    """Run a shell command and return the output."""
    env = os.environ.copy()
    env['TERM'] = 'xterm'  # Set the TERM environment variable
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    # Ensure the files directory exists
    os.makedirs(files_dir, exist_ok=True)

    # Read the JSONL file line by line
    with open(jsonl_path, 'r') as file:
        for line in file:
            # Parse the JSON line
            try:
                task = json.loads(line)
                task_id = task['id']
                input_command = task['input']
                test_command = task['test']
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in line: {line}")
                continue
            except KeyError as e:
                print(f"Error: Missing key in task: {e}")
                continue

            print(f"\nProcessing task {task_id}")

            # Unzip the corresponding zip file
            zip_path = os.path.join(files_dir, f"{task_id}.zip")
            if os.path.exists(zip_path):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(files_dir)
                    print(f"Unzipped file: {zip_path}")
                except zipfile.BadZipFile:
                    print(f"Error: {zip_path} is not a valid zip file")
                    continue
            else:
                print(f"Warning: Zip file not found for task {task_id}")

            # Execute the shell command
            print(f"Executing command: @2501 {input_command}")
            stdout, stderr, returncode = run_command(f"cd files/{task_id} && @2501 agents --flush && @2501 {input_command}")
            
            if returncode == 0:
                print(f"Command Output:\n{stdout}")
            else:
                print(f"Command failed with return code {returncode}")
                print(f"Error output:\n{stderr}")

            # Run the test command
            print(f"Running test: {test_command}")
            try:
                # Create a new dictionary with task-specific variables
                test_globals = {
                    'task_id': task_id,
                    'input_command': input_command,
                    'command_output': stdout,
                    'command_error': stderr,
                    'command_returncode': returncode
                }
                
                # Execute the test command with the task-specific globals
                output = exec(test_command, test_globals)
                print(f"Test {task_id} output: {output}")
            except Exception as e:
                print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()