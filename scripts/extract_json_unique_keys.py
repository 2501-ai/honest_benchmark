import argparse
import json


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Extract unique keys from a JSON file.')
    parser.add_argument('filepath', type=str, help='Path to the JSON file')
    args = parser.parse_args()

    # Load JSON data from file
    with open(args.filepath, 'r') as file:
        data = json.load(file)

    # Extract unique keys
    unique_keys = set(data)

    # Print the unique keys
    # fix this line to filter keys not in ['id', 'name', 'age']
    expected = [
        "occupation",
        "hobbies",
        "pets",
        "username",
        "subscription_status",
        "preferences",
        "membership_start_date",
        "first_name",
        "last_name",
        "company",
        "department",
        "years_of_experience",
        "phone",
        "last_login",
        "is_verified"
    ]

    output = len(unique_keys.difference(expected)) == 0 and len(unique_keys) == len(expected)
    assert output, f"Expected keys: {expected}, got additional fields: {list(unique_keys.difference(expected))}"


if __name__ == "__main__":
    main()
