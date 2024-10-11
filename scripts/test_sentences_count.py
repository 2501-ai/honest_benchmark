import re
import sys

def count_sentences(text):
    # Use regular expression to split the text by sentence-ending punctuation.
    sentences = re.split(r'[.!?]+', text)

    # Remove any empty strings from the resulting list
    sentences = [s for s in sentences if s.strip()]

    # Return the count of sentences
    return len(sentences)

if __name__ == "__main__":
    # Specify the path to your sample.txt file
    file_path = 'datasets/honest_28/summary.txt'  # Replace with your actual file path if needed

    try:
        # Read the content of sample.txt
        with open(file_path, 'r') as file:
            text = file.read()

        # Count the number of sentences
        sentence_count = count_sentences(text)

        print(f"The text contains {sentence_count} sentences")
        # Exit with appropriate status based on sentence count
        if sentence_count <= 2:
            sys.exit(0)  # Exit code 0 if 2 or fewer sentences
        else:
            sys.exit(1)  # Exit code 1 if more than 2 sentences

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
