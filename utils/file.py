import json
import os
import shutil


def remove_previous_folders(files_dir):
    """
    Remove all previous folders in the files directory.

    Args:
        files_dir (str): The directory containing the files.
    """
    for item in os.listdir(files_dir):
        item_path = os.path.join(files_dir, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)


def extract_tests_from_jsonl(jsonl_path):
    tests = []
    with open(jsonl_path, 'r') as file:
        for line in file:
            test = json.loads(line)
            if 'test_command' in test:
                test['test_script'] = None  # Remove 'test_script' if 'test_command' exists
            elif 'test_script' in test:
                test['test_command'] = None  # Remove 'test_command' if 'test_script' exists
            tests.append(test)
    return tests

def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading configuration: {e}")
        return {"model_pair": [], "available_models": []}