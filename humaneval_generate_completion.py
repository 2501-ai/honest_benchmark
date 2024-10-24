import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate completion.jsonl from script.py files.')
    parser.add_argument('--base_dir', type=str, required=True, help='Base directory containing numbered folders.')
    parser.add_argument('--output_file', type=str, default='completion.jsonl', help='Output file name.')
    args = parser.parse_args()

    base_dir = args.base_dir
    output_file = args.output_file

    folder_names = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        # Check if item is a directory and the name is a digit
        if os.path.isdir(item_path) and item.isdigit():
            folder_names.append(item)

    # Sort folder names numerically
    folder_names = sorted(folder_names, key=lambda x: int(x))

    with open(output_file, 'w') as f_out:
        for folder_name in folder_names:
            folder_path = os.path.join(base_dir, folder_name)
            script_path = os.path.join(folder_path, 'script.py')
            if os.path.isfile(script_path):
                with open(script_path, 'r') as f_script:
                    content = f_script.read()
                task_id = f"HumanEval/{folder_name}"
                data = {"task_id": task_id, "completion": content}
                json_line = json.dumps(data)
                f_out.write(json_line + '\n')

if __name__ == '__main__':
    main()
