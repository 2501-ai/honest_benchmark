import subprocess
import sys

# Global variable to track test results
output = ""


def run_test(test_input, expected_output, expected_code):
    """Runs the LIS script with the given test input and compares the result with the expected output."""
    global output

    # Run the longest_increasing_subsequence.py script using the test input
    result = subprocess.run(
        ['python', 'longest_increasing_subsequence.py', test_input],
        capture_output=True,
        text=True,
        cwd='./datasets/honest_24'
    )

    # Check if the process exit code is 0 (success) and validate the output
    if result.returncode != expected_code:
        output = f"FAIL (Error in execution, exit code: {result.returncode})"
        return False

    script_output = result.stdout.strip()

    if script_output != expected_output and expected_code == 0:
        output = f"FAIL (Expected: {expected_output}, but got: {script_output})"
        return False

    return True


def run_tests():
    """Runs a series of tests on the LIS solution."""
    tests = [
        ("10,9,2,5,3,7,101,18", "4", 0),
        ("3,10,2,1,20", "3", 0),
        ("1,2,3,4,5", "5", 0),
        ("5,4,3,2,1", "1", 0),
        ("", "0", 1),
        ("10,a,2,5", "", 1),
        ("1;2;3;4", "", 1),
        ("10 9 2 5", "", 1)
    ]

    all_passed = all(run_test(test_input, expected_output, expected_code) for test_input, expected_output, expected_code in tests)

    if all_passed:
        print("All tests passed!")
        sys.exit(0)
    else:
        print(f"Some tests failed! {output}")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
