# 2501 - Honest Benchmark Evaluation

This repository contains the evaluation harness for 2501 engines and mixture of models, using the script (`evaluate.py`) to evaluate tasks defined in a JSONL file. 
The script processes each task by unzipping corresponding files, executing commands, and running tests.

## Prerequisites

- Python 3.x
- 2501 CLI, [NPM repository here](https://www.npmjs.com/package/@2501-ai/2501-cli)

## Setup

On MacOS 15+, we recommend you create a virtual environment using the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
```

Then install the required packages:

```bash
pip3 install -r requirements.txt
``` 

If the installation of `psycopg2` fails, you may need to export the following environment variables:

```bash
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
```

This is a common problem with `psycopg2`, you may find more info [on stackoverflow](https://stackoverflow.com/a/66175899/1667822)

## Files and Directories

- `evaluate.py`: The main script to process and evaluate tasks.
- `honest_benchmark.jsonl`: A JSONL file containing tasks to be evaluated.
- `files/`: A directory containing zip files and other necessary files for the tasks.

## Usage

1. Ensure you have Python 3.x installed on your system.
2. Place the `config/honest_benchmark.jsonl` file in the same directory as `evaluate.py`.
3. Create a `datasets/` directory in the same location and place the corresponding zip files there.
4. Run the `evaluate.py` script:

```bash
python evaluate.py  # Reads tasks from honest_benchmark.jsonl

python evaluate.py myfile.jsonl  # Reads tasks from myfile.jsonl

python evaluate.py --test honest_24  # Runs a specific task by ID

python evaluate.py --agent-config CODING_AGENT # Runs all tasks from a specific agent config

python evaluate.py --from honest_24  # Runs all tasks from a specific task ID

```

## JSONL File Format

Each line in the `honest_benchmark.jsonl` file should be a valid JSON object with the following keys:

- `id`: A unique identifier for the task.
- `input`: The shell command to be executed.
- `test`: The test command to validate the task.

Example:

```json
{"id": "honest_1", "input": "echo 'Hello, World!'", "test": "assert 'Hello, World!' in command_output"}
```

## Results
The script will produce a ****_result.jsonl file which the results of each test and the variable `passed=True|False` added to each line. 

## Script Behavior

1. The script checks if the `files/` directory exists and creates it if it doesn't.
2. It reads the `honest_benchmark.jsonl` file line by line.
3. For each task:
   - Parses the JSON line.
   - Constructs the zip file name based on the task ID.
   - Attempts to unzip the corresponding zip file in the `files/` directory.
   - Executes the shell command specified in the `input` key using `subprocess.run()`.
   - Runs the test command specified in the `test` key using Python's `exec()` function.
   - Prints the results of the task execution and test.

## Security Considerations

- The script uses `subprocess.run()` with `shell=True`, which can be a security risk if the input is not properly sanitized. Ensure that the `input` commands in the JSONL file are from trusted sources.
- The `test` commands are executed using Python's `exec()` function, which can also be a security risk. Make sure the test commands are safe and from trusted sources.

## Limitations

- The script assumes that all necessary dependencies for running the tasks are already installed on the system.
- There's no built-in timeout mechanism for long-running tasks, which could potentially cause the script to hang.

## Contributing

Contributions to improve the script or documentation are welcome. Please submit a pull request or open an issue to discuss proposed changes.

## License

This project is open-source and available under the MIT License.