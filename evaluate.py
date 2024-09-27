import argparse
import os
import signal
import sys

from benchmark_report import BenchmarkReport
from task_processor import process_task
from utils.file import remove_previous_folders, extract_tests_from_jsonl


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
    for task in tests:
        if testnum and task['id'] != testnum:
            continue
        if testfrom and not is_test_from:
            if task['id'] == testfrom:
                is_test_from = True
            else:
                continue

        benchmark.add_test(task['id'], task.get('description', ''))
        process_task(task, dataset_dir, benchmark, max_retries=benchmark.retry_limit)

    # Save the results and metadata
    benchmark.save_to_file()


def signal_handler(sig, frame):
    print('You pressed CTRL+C! Exiting...')
    # Perform any necessary cleanup here
    sys.exit(0)

# Register the signal handler for SIGINT (CTRL+C)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate tasks from a JSONL file.')
    parser.add_argument('problem_file', type=str, help='Path to the JSONL file containing the tasks.', nargs='?',
                        default='./config/honest_benchmark.jsonl')
    parser.add_argument('--benchmark-config', type=str, help='Path to the benchmark configuration file.',
                        default='./config/benchmark_config.json', dest='benchmark_config')
    parser.add_argument('--test', type=str, help='Test ID to run.', default=None, dest='testnum')
    parser.add_argument('--from', type=str, help='Test ID to run from.', default=None, dest='testfrom')
    args = parser.parse_args()
    main(args.problem_file, args.benchmark_config, args.testnum, args.testfrom)
