import argparse
import logging
import os
import signal
import sys
from multiprocessing import Pool, cpu_count

from benchmark_report import BenchmarkReport
from task_processor import process_task
from utils.file import remove_previous_folders, extract_tests_from_jsonl

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_task_wrapper(args):
    """
    Wrapper function for parallel processing of tasks.

    Args:
        args (tuple): Contains (task, dataset_dir, retry_limit, agent_config)
    """
    task, dataset_dir, retry_limit, agent_config = args
    return process_task(task, dataset_dir, retry_limit, agent_config)


def handle_result(result_entry, benchmark, task_id=None, fail_fast=False):
    """
    Handle the result of a task execution.

    Args:
        result_entry (dict): The result entry from task processing
        benchmark (BenchmarkReport): The benchmark report instance
        task_id (str, optional): The task ID for better error reporting
        fail_fast (bool): Whether to exit immediately when a test fails
    """
    benchmark.add_result(result_entry)
    if not result_entry["passed"] and fail_fast:
        task_info = f" {task_id}" if task_id else ""
        logging.error(
            f"\nTest{task_info} failed after {benchmark.retry_limit} retries. Exiting due to --fail-fast."
        )
        logging.error(f"Error message: {result_entry.get('error_message')}")
        benchmark.save_to_file()
        sys.exit(1)


def main(
    jsonl_path,
    benchmark_config,
    agent_config,
    testnum,
    testfrom,
    fail_fast,
    parallel,
    description,
):
    """
    Main function to process tasks from a JSONL file.

    Args:
        jsonl_path (str): Path to the JSONL file containing the tasks.
        benchmark_config (str): Path to the benchmark configuration file.
        agent_config (str): Agent configuration to use.
        testnum (str): Specific test ID to run.
        testfrom (str): Test ID to start running from.
        fail_fast (bool): Whether to exit immediately when a test fails.
        parallel (int): Number of parallel workers (0 means use CPU count, 1 means sequential).
        description (str): Optional description of the benchmark run.
    """
    dataset_dir = "datasets"
    remove_previous_folders(dataset_dir)
    os.makedirs(dataset_dir, exist_ok=True)

    # Load benchmark configuration
    benchmark = BenchmarkReport(
        "AI Model Pair Benchmark", config_file=benchmark_config, description=description
    )
    tests = extract_tests_from_jsonl(jsonl_path)

    # Filter tests based on testnum and testfrom
    filtered_tests = []
    is_test_from = False
    for task in tests:
        if testnum and task["id"] != testnum:
            continue
        if testfrom and not is_test_from:
            if task["id"] == testfrom:
                is_test_from = True
            else:
                continue
        filtered_tests.append(task)
        benchmark.add_test(task)

    # Always use parallel processing
    # Prepare arguments for parallel processing
    process_args = [
        (task, dataset_dir, benchmark.retry_limit, agent_config)
        for task in filtered_tests
    ]

    # Use specified number of workers or CPU count if parallel is 0
    num_processes = parallel or cpu_count()
    # Cap number of processes at number of tests
    num_processes = min(num_processes, len(filtered_tests))
    logging.info(f"Running {num_processes} processes in parallel")

    with Pool(num_processes) as pool:
        # Use imap_unordered for non-blocking iteration over results
        for result_entry in pool.imap_unordered(process_task_wrapper, process_args):
            handle_result(result_entry, benchmark, fail_fast=fail_fast)

    # Save the results and metadata
    benchmark.save_to_file()


def signal_handler(sig, frame):
    logging.warning("You pressed CTRL+C! Exiting...")
    # Perform any necessary cleanup here
    sys.exit(0)


# Register the signal handler for SIGINT (CTRL+C)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate tasks from a JSONL file.")
    parser.add_argument(
        "problem_file",
        type=str,
        help="Path to the JSONL file containing the tasks.",
        nargs="?",
        default="./config/honest_benchmark.jsonl",
    )
    parser.add_argument(
        "--benchmark-config",
        type=str,
        help="Path to the benchmark configuration file.",
        default="./config/benchmark_config.json",
        dest="benchmark_config",
    )
    parser.add_argument(
        "--test", type=str, help="Test ID to run.", default=None, dest="testnum"
    )
    parser.add_argument(
        "--from", type=str, help="Test ID to run from.", default=None, dest="testfrom"
    )
    parser.add_argument(
        "--agent-config",
        type=str,
        help="Agent to run.",
        default="CODING_AGENT",
        dest="agent_config",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit immediately if a test fails after all retries",
        dest="fail_fast",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=0,
        help="Number of parallel workers. 0=use CPU count (default), N=N workers)",
        dest="parallel",
    )
    parser.add_argument(
        "--description",
        type=str,
        default=None,
        help="Optional description of the benchmark run",
        dest="description",
    )
    args = parser.parse_args()

    # Print all arguments
    logging.info("\nRunning with arguments:")
    for arg, value in vars(args).items():
        logging.info(f"  {arg}: {value}")

    main(
        args.problem_file,
        args.benchmark_config,
        args.agent_config,
        args.testnum,
        args.testfrom,
        args.fail_fast,
        args.parallel,
        args.description,
    )
