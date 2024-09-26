import argparse
import os

from lib import BenchmarkReport, extract_tests_from_jsonl
from task_processor import process_task
from utils.file import remove_previous_folders


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
    result_dir = 'results'

    remove_previous_folders(dataset_dir)
    os.makedirs(dataset_dir, exist_ok=True)
    os.makedirs(result_dir, exist_ok=True)

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

        result_jsonl_path = os.path.join(result_dir, f'{task["id"]}_result.jsonl')
        process_task(task, dataset_dir, result_jsonl_path, max_retries=benchmark.retry_limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate tasks from a JSONL file.')
    parser.add_argument('problem_file', type=str, help='Path to the JSONL file containing the tasks.', nargs='?',
                        default='honest_benchmark.jsonl')
    parser.add_argument('--benchmark-config', type=str, help='Path to the benchmark configuration file.',
                        default='benchmark_config.json', dest='benchmark_config')
    parser.add_argument('--test', type=str, help='Test ID to run.', default=None, dest='testnum')
    parser.add_argument('--from', type=str, help='Test ID to run from.', default=None, dest='testfrom')
    args = parser.parse_args()
    main(args.problem_file, args.benchmark_config, args.testnum, args.testfrom)
