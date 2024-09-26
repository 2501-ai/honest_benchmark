import json
import os


def convert_test_format(input_file, output_file):
    """
    Convert test JSONL old file format to include 'test_script' and other updates.

    Args:
        input_file (str): Path to the input JSONL file.
        output_file (str): Path to the output JSONL file.
    """
    os.makedirs('./scripts', exist_ok=True)

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            test = json.loads(line)
            # Determine the test script content
            if 'test' in test:
                # Save the test script content to a file
                # script_filename = f'./scripts/{test["id"]}.py'
                # with open(script_filename, 'w') as script_file:
                #     script_file.write(test['test'])

                # Update test dictionary
                test['test_script'] = (test['test'])
                test.pop('test', None)
            else:
                test['test_script'] = None  # No test script content

            # Convert 'labels' to 'tags' and handle other field removals
            if 'labels' in test:
                test['tags']  = test.pop('labels'),
            else:
                test['tags'] = []

            # Remove old 'status' field if present
            test.pop('status', None)

            # Write updated test to output file
            outfile.write(json.dumps(test) + '\n')


def extract_expected_output(test_code):
    """
    Extract the expected output from the test code.

    Args:
        test_code (str): The test code string.

    Returns:
        str: Extracted expected output.
    """
    # Simple heuristic: Extract the output condition from the test code
    if "PASS" in test_code:
        return "PASS"
    elif "FAIL" in test_code:
        return "FAIL"
    return "UNKNOWN"


if __name__ == "__main__":
    input_path = 'honest_benchmark_old.jsonl'
    output_path = 'honest_benchmark.jsonl'
    convert_test_format(input_path, output_path)
