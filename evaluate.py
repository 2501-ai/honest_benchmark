import argparse
import os
import signal
import sys
import multiprocessing
import time
from functools import partial

from benchmark_report import BenchmarkReport
from task_processor import process_task
from utils.file import remove_previous_folders, extract_tests_from_jsonl
from utils.db_connection import DBConnector

def process_task_wrapper(args):
    """Wrapper function for multiprocessing that returns the result"""
    task, dataset_dir, max_retries = args
    start_time = time.time()
    result = process_task(task, dataset_dir, max_retries=max_retries)
    duration_ms = int((time.time() - start_time) * 1000)
    return {
        'task': task,
        'result': result,
        'duration_ms': duration_ms
    }

def main(jsonl_path, benchmark_config, testnum, testfrom, n_jobs=1):
    """
    Main function to process tasks from a JSONL file.

    Args:
        jsonl_path (str): Path to the JSONL file containing the tasks.
        benchmark_config (str): Path to the benchmark configuration file.
        testnum (str): Specific test ID to run.
        testfrom (str): Test ID to start running from.
        n_jobs (int): Number of parallel jobs. If 0 or 1, runs sequentially.
    """
    dataset_dir = 'datasets'
    remove_previous_folders(dataset_dir)
    os.makedirs(dataset_dir, exist_ok=True)

    # Load benchmark configuration
    benchmark = BenchmarkReport("AI Model Pair Benchmark", config_file=benchmark_config)

    # Load tests
    tests = extract_tests_from_jsonl(jsonl_path)

    # Filter tasks based on testnum and testfrom
    filtered_tasks = []
    is_test_from = False
    for task in tests:
        if testnum and task['id'] != testnum:
            continue
        if testfrom and not is_test_from:
            if task['id'] == testfrom:
                is_test_from = True
            else:
                continue
        filtered_tasks.append(task)
        benchmark.add_test(task)

    # Process tasks either sequentially or in parallel
    if n_jobs <= 1:
        # Sequential processing
        db_connector = DBConnector()
        for task in filtered_tasks:
            result = process_task(task, dataset_dir, max_retries=benchmark.retry_limit)
            
            # Add results to benchmark report if result exists
            if result:
                benchmark.add_result(
                    task_id=task['id'],
                    input_command=task['input'],
                    script=task.get('test_command', '') or task.get('test_script', ''),
                    passed=result.get('passed', False),
                    retries=result.get('retries', 0),
                    duration_ms=result.get('duration_ms', 0),
                    accuracy=result.get('accuracy', 0),
                    error_message=result.get('error_message')
                )
            
            # Store results in database after each task
            last_test = benchmark.existing_data['tests'][-1]
            last_result = last_test['results'][-1]
            passed = all(result['passed'] for result in last_test['results'])
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
    else:
        # Parallel processing
        n_jobs = min(n_jobs, len(filtered_tasks))
        task_args = [(task, dataset_dir, benchmark.retry_limit) 
                    for task in filtered_tasks]
        
        # Using 'with' to ensure pool is properly closed and joined even if an error occurs
        with multiprocessing.Pool(processes=n_jobs) as pool:
            results = pool.map(process_task_wrapper, task_args)
            
        # Process results in the main process
        for result_data in results:
            task = result_data['task']
            result = result_data['result']
            duration_ms = result_data['duration_ms']
            
            # Add results to benchmark report
            if result:
                benchmark.add_result(
                    task_id=task['id'],
                    input_command=task['input'],
                    script=task.get('test_command', '') or task.get('test_script', ''),
                    passed=result.get('passed', False),
                    retries=result.get('retries', 0),
                    duration_ms=duration_ms,
                    accuracy=result.get('accuracy', 0),
                    error_message=result.get('error_message')
                )

    # Save the results and metadata
    benchmark.save_to_file()

def signal_handler(sig, frame):
    print('You pressed CTRL+C! Exiting...')
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
    parser.add_argument('--parallel', type=int, help='Number of parallel processes to use. Default is 1 (sequential).',
                        default=1, dest='n_jobs')
    args = parser.parse_args()
    main(args.problem_file, args.benchmark_config, args.testnum, args.testfrom, args.n_jobs)
