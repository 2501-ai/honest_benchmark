import argparse
import json


def extract_unique_keys(data, keys_set=None):
    if keys_set is None:
        keys_set = set()

    if isinstance(data, dict):
        for key, value in data.items():
            keys_set.add(key)
            extract_unique_keys(value, keys_set)
    elif isinstance(data, list):
        for item in data:
            extract_unique_keys(item, keys_set)

    return keys_set


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Extract unique keys from a JSON file.')
    parser.add_argument('filepath', type=str, help='Path to the JSON file')
    args = parser.parse_args()

    # Load JSON data from file
    with open(args.filepath, 'r') as file:
        data = json.load(file)

    # Extract unique keys
    unique_keys = extract_unique_keys(data)

    # Print the unique keys
    print("Unique keys found in the JSON file:")
    for key in sorted(unique_keys):
        print(key)


if __name__ == "__main__":
    main()
