import json


def write_result(task, passed, result_jsonl_path, error_message=None, retries=0):
    """
    Write the result to the result JSONL file.

    Args:
        task (dict): The task dictionary.
        passed (bool): Whether the task passed or not.
        result_jsonl_path (str): Path to the result JSONL file.
        error_message (str): Error message if any.
        retries (int): Number of retries done.
    """
    task['passed'] = passed
    task['retries'] = retries
    if error_message:
        task['error'] = error_message
    if 'test_command' in task:
        task['test_script'] = task.pop('test_command')
    if 'test_script' in task:
        task['script'] = task.pop('test_script')
    task.pop('status', None)
    with open(result_jsonl_path, 'a') as result_file:
        result_file.write(json.dumps(task) + '\n')
