import json
from datetime import datetime

from utils.file import load_config


class BenchmarkReport:
    def __init__(self, benchmark_name, config_file='benchmark_config.json', retry_limit=3):
        self.benchmark_name = benchmark_name
        self.retry_limit = retry_limit
        self.model_pairs = []
        self.tests = []  # Initialize the tests field
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.summary = {
            "total_tests": 0,
            "total_results": 0,
            "completed_tests": 0,
            "failed_tests": 0,
            "average_duration_ms": 0.0,
            "average_accuracy": 0.0,
            "overall_metrics": {
                "max_duration_ms": 0.0,
                "min_duration_ms": float('inf'),
                "max_accuracy": 0.0,
                "min_accuracy": 1.0
            }
        }
        self.config = load_config(config_file)
        self.model_pairs = self.config.get('model_pairs', [])

    def add_test(self, test_name, description):
        """
        Add a new test entry to the benchmark report.

        Args:
            test_name (str): The name of the test.
            description (str): The description of the test.
        """
        # Append the test entry to the tests list
        self.tests.append({
            "test_name": test_name,
            "description": description,
            "results": []
        })

    def add_result(self, task_id, input_command, script, passed, retries, duration_ms=0, accuracy=None,
                   error_message=None):
        """
        Add the result of a task to the most recent test in the report.

        Args:
            task_id (str): The ID of the task.
            input_command (str): The input command executed.
            script (str): The test script path or inline test script.
            passed (bool): Whether the task passed or failed.
            retries (int): The number of retries performed.
            duration_ms (int, optional): Duration of the test in milliseconds.
            accuracy (float, optional): Accuracy of the result. Defaults to 1.0 if passed, 0.0 otherwise.
            error_message (str, optional): Any error message if the test failed.
        """
        if not self.tests:
            print("No test has been added to attach this result.")
            return

        # Determine accuracy if not provided
        if accuracy is None:
            accuracy = 1.0 if passed else 0.0

        result_entry = {
            'id': task_id,
            'input': input_command,
            'script': script,
            'passed': passed,
            'retries': retries,
            'error_message': error_message,
            'metrics': {
                'accuracy': accuracy,
                'duration_ms': duration_ms  # Pass duration here
            }
        }

        # Append the result to the most recent test
        self.tests[-1]['results'].append(result_entry)

        # Update summary after adding the result
        self._update_summary()

    def _update_summary(self):
        total_duration = 0
        total_accuracy = 0
        completed_tests = 0
        failed_tests = 0

        for test in self.tests:
            for result in test['results']:
                duration = result['metrics'].get('duration_ms', 0) or 0  # Ensure duration is not None
                accuracy = result['metrics'].get('accuracy', 0) or 0  # Ensure accuracy is not None

                if result['passed']:
                    completed_tests += 1
                    total_duration += duration
                    total_accuracy += accuracy

                    # Update max/min duration and accuracy metrics
                    if duration > self.summary['overall_metrics']['max_duration_ms']:
                        self.summary['overall_metrics']['max_duration_ms'] = duration
                    if duration < self.summary['overall_metrics']['min_duration_ms']:
                        self.summary['overall_metrics']['min_duration_ms'] = duration
                    if accuracy > self.summary['overall_metrics']['max_accuracy']:
                        self.summary['overall_metrics']['max_accuracy'] = accuracy
                    if accuracy < self.summary['overall_metrics']['min_accuracy']:
                        self.summary['overall_metrics']['min_accuracy'] = accuracy
                else:
                    failed_tests += 1

        self.summary['total_tests'] = len(self.tests)
        self.summary['total_results'] = sum(len(test['results']) for test in self.tests)
        self.summary['completed_tests'] = completed_tests
        self.summary['failed_tests'] = failed_tests

        if completed_tests > 0:
            self.summary['average_duration_ms'] = total_duration / completed_tests
            self.summary['average_accuracy'] = total_accuracy / completed_tests

    def save_to_file(self, output_dir):
        """
        Save the benchmark report to a JSON file.

        Args:
            output_dir (str): The directory where the report will be saved.
        """
        data = {
            "benchmark": self.benchmark_name,
            "date": self.date,
            "retry_limit": self.retry_limit,
            "model_pairs": self.model_pairs,
            "tests": self.tests,
            "summary": self.summary
        }
        output_path = f"{output_dir}/benchmark_report_{self.date}.json"
        with open(output_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Benchmark report saved to {output_path}")