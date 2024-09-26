import json
from datetime import datetime


class BenchmarkReport:
    def __init__(self, benchmark_name, config_file='benchmark_config.json', retry_limit=3):
        self.benchmark_name = benchmark_name
        self.retry_limit = retry_limit
        self.model_pairs = []
        self.tests = []
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
        self.config = self.load_config(config_file)
        self.model_pairs = self.config.get('model_pairs', [])

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading configuration: {e}")
            return {"model_pairs": [], "available_models": []}

    def add_test(self, test_name, description, results):
        self.tests.append({
            "test_name": test_name,
            "description": description,
            "results": results
        })
        self._update_summary()

    def _update_summary(self):
        total_duration = 0
        total_accuracy = 0
        completed_tests = 0
        failed_tests = 0

        for test in self.tests:
            for result in test['results']:
                if result['status'] == 'completed':
                    completed_tests += 1
                    total_duration += result.get('duration_ms', 0)
                    total_accuracy += result['metrics'].get('accuracy', 0)
                    if result.get('duration_ms', 0) > self.summary['overall_metrics']['max_duration_ms']:
                        self.summary['overall_metrics']['max_duration_ms'] = result['duration_ms']
                    if result.get('duration_ms', 0) < self.summary['overall_metrics']['min_duration_ms']:
                        self.summary['overall_metrics']['min_duration_ms'] = result['duration_ms']
                    if result['metrics'].get('accuracy', 0) > self.summary['overall_metrics']['max_accuracy']:
                        self.summary['overall_metrics']['max_accuracy'] = result['metrics']['accuracy']
                    if result['metrics'].get('accuracy', 0) < self.summary['overall_metrics']['min_accuracy']:
                        self.summary['overall_metrics']['min_accuracy'] = result['metrics']['accuracy']
                else:
                    failed_tests += 1

        self.summary['total_tests'] = len(self.tests)
        self.summary['total_results'] = sum(len(test['results']) for test in self.tests)
        self.summary['completed_tests'] = completed_tests
        self.summary['failed_tests'] = failed_tests
        if completed_tests > 0:
            self.summary['average_duration_ms'] = total_duration / completed_tests
            self.summary['average_accuracy'] = total_accuracy / completed_tests

    def save_to_file(self, filename):
        data = {
            "benchmark": self.benchmark_name,
            "date": self.date,
            "retry_limit": self.retry_limit,
            "model_pairs": self.model_pairs,
            "tests": self.tests,
            "summary": self.summary
        }
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

def extract_tests_from_jsonl(jsonl_path):
    tests = []
    with open(jsonl_path, 'r') as file:
        for line in file:
            test = json.loads(line)
            if 'script_path' in test:
                test['test_script'] = None  # Remove 'test_script' if 'script_path' exists
            elif 'test_script' in test:
                test['script_path'] = None  # Remove 'script_path' if 'test_script' exists
            tests.append(test)
    return tests