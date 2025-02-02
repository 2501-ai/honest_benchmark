import json
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

from utils.db_connection import DBConnector	
from utils.file import load_config


class BenchmarkReport:
    existing_data: dict[str, any]

    def __init__(self, benchmark_name, config_file='./config/benchmark_config.json', retry_limit=3):
        load_dotenv('.env')
        self.benchmark_name = benchmark_name
        self.retry_limit = retry_limit
        self.date = datetime.now().strftime('%Y-%m-%d')
        self.run_at = datetime.now(timezone.utc).isoformat()
        self.timestamp_ms = datetime.now().timestamp()

        self.id = str(uuid.uuid4())
        print(f"Benchmark report id, benchmark_id={self.id}")
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
        self.model_pair = [os.getenv('MAIN_ENGINE'), os.getenv('SECONDARY_ENGINE')]
        self.pre_process_model = 'META_LLAMA3_70B_CEREBRAS'
        self.tests: list = []
        self.config = load_config(config_file)
        self.reset = self.config.get('reset',
                                     True)  # Reset the Benchmark results if True, else append the results for stats.
        self.output_path = f"./results/benchmark_report_{self.date}.json"

        if os.path.exists(self.output_path) and not self.reset:
            with open(self.output_path, 'r') as file:
                self.existing_data = json.load(file)
        else:
            self.existing_data = {
                "benchmark": self.benchmark_name,
                "date": self.date,
                "retry_limit": self.retry_limit,
                "model_pair": self.model_pair,
                "benchmark_file": config_file,
                "run_at": self.run_at,
                "tests": [],
                "summary": self.summary
            }

    def add_test(self, task):
        """
        Add a new test entry to the benchmark report.

        Args:
            task (dict): The task dictionary containing the test details.
        """
        # Append the test entry to the tests list
        test_exists = any(test['name'] == task['id'] for test in self.existing_data['tests'])
        if not test_exists:
            self.existing_data['tests'].append({
                "name": task['id'],
                "tags": task['tags'],
                "results": []
            })

    def add_result(self, result_entry):
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

        for test in self.existing_data.get('tests', []):
            if test['name'] == result_entry['task_id']:
                result_entry['benchmark_id'] = self.id
                result_entry['labels'] = test['tags']
                result_entry['pre_process_model'] = self.pre_process_model
                result_entry['model_pair'] = self.model_pair

                # Append the result to the specified test
                test['results'].append(result_entry)
                break
        else:
            raise ValueError(f"Test with name '{result_entry['task_id']}' does not exist. Add the test before adding results.")

        # Update summary after adding the result
        self._update_summary()

        # Aggregate results for each test and store in the database
        passed = all(result['passed'] for result in test['results'])

        # Store results in database
        total_duration = sum(result['metrics']['duration_ms'] for result in test['results'])
        average_accuracy = sum(result['metrics']['accuracy'] for result in test['results']) / len(test['results'])
        db_connector = DBConnector()
        db_connector.connect()
        db_connector.store_benchmark_result({
            'task_id': test['name'],
            'task_name': test['name'],
            'benchmark_id': self.id,
            'input': result_entry['input_command'],
            'passed': passed,
            'labels': result_entry['labels'],
            'duration_ms': total_duration,
            'pre_process_model': self.pre_process_model,
            'model_pair': self.model_pair,
            'accuracy': average_accuracy,
            'run_at': self.run_at,
            'benchmark_file': self.config_file,
            'test': test,
            'error_message': result_entry.get('error_message')
        })
        db_connector.close_connection()

    def _update_summary(self):
        total_duration = 0
        total_accuracy = 0
        completed_tests = 0
        failed_tests = 0
        test_durations = {}

        for test in self.existing_data.get('tests', []):
            for result in test['results']:
                duration = result['metrics'].get('duration_ms', 0) or 0  # Ensure duration is not None
                accuracy = result['metrics'].get('accuracy', 0) or 0  # Ensure accuracy is not None

                if result['passed']:
                    completed_tests += 1
                    if test['name'] not in test_durations:
                        test_durations[test['name']] = 0
                    test_durations[test['name']] += duration
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

        self.summary['total_tests'] = len(self.existing_data.get('tests', []))
        self.summary['total_results'] = sum(len(test['results']) for test in self.existing_data.get('tests', []))
        self.summary['completed_tests'] = completed_tests
        self.summary['failed_tests'] = failed_tests

        if completed_tests > 0:
            self.summary['average_duration_ms'] = total_duration / completed_tests
            self.summary['average_accuracy'] = total_accuracy / completed_tests

    def save_to_file(self):
        """
        Save the benchmark report to a JSON file.
        """

        # Ensure the directory exists
        directory = os.path.dirname(self.output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        self._update_summary()

        # Save the updated data to a file
        with open(self.output_path, 'w') as file:
            json.dump(self.existing_data, file, indent=4)
        print(f"Benchmark report saved to {self.output_path}")

        print(f"Benchmark summary:\n{json.dumps(self.summary)}")
