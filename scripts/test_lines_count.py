# Define the path to the file
import sys

file_path = './datasets/honest_47/list.txt'

# Initialize a counter for non-empty lines
output = 0


def main():
    global output
    # Open the file and count non-empty lines
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Check if the line has text (is not empty or whitespace)
                output += 1

    # Print the count of lines with text
    print(f'Number of lines with text: {output}')
    if output == 9:
        # Exit with code 0 if the output is correct
        sys.exit(0)
    else:
        # Return a code 1 if the output is incorrect
        sys.exit(1)


if __name__ == "__main__":
    main()
