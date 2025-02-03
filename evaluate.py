import argparse
import os
import signal
import sys

from benchmark_report import BenchmarkReport
from task_processor import process_task
from utils.file import remove_previous_folders, extract_tests_from_jsonl
from utils.db_connection import DBConnector


def main(jsonl_path, benchmark_config, agent_config, testnum, testfrom, fail_fast):
    """
    Main function to process tasks from a JSONL file.

    Args:
        jsonl_path (str): Path to the JSONL file containing the tasks.
        benchmark_config (str): Path to the benchmark configuration file.
        agent_config (str): Agent configuration to use.
        testnum (str): Specific test ID to run.
        testfrom (str): Test ID to start running from.
        fail_fast (bool): Whether to exit immediately when a test fails.
    """
    dataset_dir = 'datasets'
    remove_previous_folders(dataset_dir)
    os.makedirs(dataset_dir, exist_ok=True)

    # Load benchmark configuration
    benchmark = BenchmarkReport("AI Model Pair Benchmark", config_file=benchmark_config)
    tests = extract_tests_from_jsonl(jsonl_path)
    
    exit_with_failure = False
    is_test_from = False
    db_connector = DBConnector()

    for task in tests:
        if testnum and task['id'] != testnum:
            continue
        if testfrom and not is_test_from:
            if task['id'] == testfrom:
                is_test_from = True
            else:
                continue

        benchmark.add_test(task)
        result_entry = process_task(task, dataset_dir, benchmark.retry_limit, agent_config)
        benchmark.add_result(result_entry)

        # Aggregate results for each test and store in the database
        last_test = benchmark.existing_data['tests'][-1]
        last_result = last_test['results'][-1]
        passed = all(result['passed'] for result in last_test['results'])
        
        # Store results in database
        total_duration = sum(result['metrics']['duration_ms'] for result in last_test['results'])
        average_accuracy = sum(result['metrics']['accuracy'] for result in last_test['results']) / len(last_test['results'])
        db_connector.connect()
        db_connector.store_benchmark_result({
            'task_id': last_test['name'],
            'task_name': last_test['name'],
            'benchmark_id': benchmark.id,
            'input': last_result['input_command'],
            'passed': passed,
            'labels': last_result['labels'],
            'duration_ms': total_duration,
            'pre_process_model': benchmark.pre_process_model,
            'model_pair': benchmark.model_pair,
            'accuracy': average_accuracy,
            'run_at': benchmark.run_at,
            'benchmark_file': benchmark_config,
            'test': last_test,
            'error_message': last_result.get('error_message')
        })
        db_connector.close_connection()

        if not passed and fail_fast:
            exit_with_failure = True
            print(f"\nTest {task['id']} failed after {benchmark.retry_limit} retries. Exiting due to --fail-fast.")
            print(f"Error message: {last_result.get('error_message')}")
            break  # Exit the 

    # Save the results and metadata
    benchmark.save_to_file()
    
    if exit_with_failure: # exit with 1 only if fail-fast is enabled
        sys.exit(1)


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
    parser.add_argument('--agent-config', type=str, help='Agent to run.', default='CODING_AGENT', dest='agent_config')
    parser.add_argument('--fail-fast', action='store_true',
                       help='Exit immediately if a test fails after all retries', 
                       dest='fail_fast')
    args = parser.parse_args()
    main(args.problem_file, args.benchmark_config, args.agent_config, args.testnum, args.testfrom, args.fail_fast)
