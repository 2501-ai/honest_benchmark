import argparse
import os
import signal
import sys
from pathlib import Path

from benchmark_report import BenchmarkReport
from task_processor import process_task
from utils.file import remove_previous_folders, extract_tests_from_jsonl
from utils.db_connection import DBConnector
from utils.command import run_command
from concurrent.futures import ThreadPoolExecutor, as_completed

test_prompt = """
complete the script.py file in the workspace following its instructions. 

test the new script with doctest, example : python -m doctest -v script.py
- if the test fails, fix and retry until it passes the test,
- if the test pass, goes to the next one and so on...,
- if the test pass BUT there is no test apparently,
- fix the doctest in the script and retry until it passes with test, some doctest are not well formatted on purpose,
think about edgy cases if you need to add some tests.
- beware the types of returns (string, int, etc.)

don't remove the breaklines at the beginning and the end of the script, they are necessary for the tests to pass
don't write tests in the script, they should be only written in the doctest

IMPORTANT : no item shoud have no tests and all should pass. 
doctest output examples : 
1 items had no tests >> NOT GOOD
2 passed and 1 failed >> NOT GOOD
0 passed and 0 failed >> NOT GOOD
all tests passed >> GOOD
"""

def main(jsonl_path, benchmark_config, testnum, testfrom):
    """
    Main function to process tasks from a JSONL file.

    Args:
        jsonl_path (str): Path to the JSONL file containing the tasks.
        benchmark_config (str): Path to the benchmark configuration file.
        testnum (str): Specific test ID to run.
        testfrom (str): Test ID to start running from.
    """
    dataset_dir = 'datasets'
    remove_previous_folders(dataset_dir)

    os.makedirs(dataset_dir, exist_ok=True)

    # Load benchmark configuration
    benchmark = BenchmarkReport("AI Model Pair Benchmark", config_file=benchmark_config)

    # Load tests
    tests = extract_tests_from_jsonl(jsonl_path)

    is_test_from = False

    def process_single_task(task):
        task_id = task['task_id']
        task_prompt = task['prompt']
        # Ensure the directory exists
        output_file = Path(f'./humaneval/{task_id}/script.py')
        output_file.parent.mkdir(exist_ok=True, parents=True)
        output_file.write_text(task_prompt)
        
        print(f"Executing {task_id}")
        run_command(f"@2501 set engine env && @2501 agents --flush")
        stdout, stderr, returncode = run_command(f"export NODE_ENV=dev && cd ./humaneval/{task_id} && @2501 \"{test_prompt}\"")
        print(stderr)
        return task_id, stdout, stderr

    tasks_to_process = []
    for task in tests:
        if testnum and task['task_id'] != testnum:
            continue
        if testfrom and not is_test_from:
            if task['task_id'] == testfrom:
                is_test_from = True
            else:
                continue
        tasks_to_process.append(task)

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_task = {executor.submit(process_single_task, task): task for task in tasks_to_process}
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                task_id, stdout, stderr = future.result()
                print(f"Task {task_id} completed | stdout: {stdout}")
            except Exception as exc:
                print(f"Task {task['task_id']} generated an exception: {exc}")

def signal_handler(sig, frame):
    print('You pressed CTRL+C! Exiting...')
    # Perform any necessary cleanup here
    sys.exit(0)

# Register the signal handler for SIGINT (CTRL+C)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate tasks from a JSONL file.')
    parser.add_argument('--problem-file', type=str, help='Path to the JSONL file containing the tasks.', nargs='?',
                        default='./config/honest_benchmark.jsonl')
    parser.add_argument('--benchmark-config', type=str, help='Path to the benchmark configuration file.',
                        default='./config/benchmark_config.json', dest='benchmark_config')
    parser.add_argument('--test', type=str, help='Test ID to run.', default=None, dest='testnum')
    parser.add_argument('--from', type=str, help='Test ID to run from.', default=None, dest='testfrom')
    args = parser.parse_args()
    main(args.problem_file, args.benchmark_config, args.testnum, args.testfrom)
