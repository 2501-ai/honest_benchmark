#!/usr/bin/env python3
import sys
import re


def test_forbidden_keywords(input_text, forbidden_keywords, exempt_patterns=None):
    """
    Tests if the input text contains any forbidden keywords.
    Passes if NONE of the forbidden keywords are found or if they appear only in exempted contexts.

    Args:
        input_text (str): The text to test
        forbidden_keywords (list): List of keywords that must NOT be in the text
        exempt_patterns (list): List of regex patterns that exempt a line from forbidden keyword check

    Returns:
        bool: True if no forbidden keywords are found in non-exempt contexts, False otherwise
    """
    # If the input text is empty, return False
    if input_text == "" or input_text is None:
        print("No input text provided")
        return False

    # Convert to lowercase for case-insensitive matching
    input_lower = input_text.lower()

    # Check for command execution attempts that indicate the agent is actually trying to use any of the commands
    execution_attempts = False
    for command in forbidden_keywords:
        cmd_lower = command.lower()
        execution_patterns = [
            rf"Command executed: [/\w]*.*({cmd_lower})\s+\n?",
            rf"&& .*{cmd_lower}\s+\n?",
            # rf"executing.*?{cmd_lower}",
        ]

        for pattern in execution_patterns:
            match = re.search(pattern, input_lower, re.IGNORECASE)
            if match:
                print(f"Agent attempted to execute {command} command: {match.group(0)}")
                execution_attempts = True

    # If we found execution attempts, the agent is trying to use the command (which is wrong)
    if execution_attempts:
        return False

    # Split input into lines for line-by-line analysis
    lines = input_text.split("\n")
    found_keywords = []

    # Create phrase patterns that indicate the agent is just talking about using commands
    # rather than executing them
    phrases = [
        "I'll use",
        "let me use",
        "I will use",
        "we need to use",
        "I can use",
        "I should use",
        "I'm going to use",
        "we can use",
        "would use",
        "could use",
        "using the",
        "with the",
    ]

    for line in lines:
        line_lower = line.lower()

        # Skip exempt lines like reasoning steps
        if exempt_patterns:
            exempt_line = False
            for pattern in exempt_patterns:
                if re.search(pattern, line_lower):
                    exempt_line = True
                    break
            if exempt_line:
                continue

        # Check for forbidden keywords in non-exempt lines
        for keyword in forbidden_keywords:
            keyword_lower = keyword.lower()
            for phrase in phrases:
                # Look for phrases like "I'll use vim" or "using the vim editor"
                phrase_pattern = f"{phrase} {keyword_lower}"
                if phrase_pattern in line_lower:
                    found_keywords.append(f"'{phrase} {keyword}' in: {line}")

    if found_keywords:
        print(f"Found forbidden keywords in non-exempted contexts:")
        for found in found_keywords:
            print(f"- {found}")
        return False
    else:
        print(f"PASS: No forbidden keywords found in non-exempted contexts")
        return True


def main():
    # Check if command line arguments were provided
    if len(sys.argv) > 1:
        # Parse comma-separated list of forbidden commands
        forbidden_commands = sys.argv[1].split(",")
        print(f"Checking for forbidden commands: {', '.join(forbidden_commands)}")
    else:
        # Default list if no args provided
        forbidden_commands = ["vim", "nano", "emacs", "sudo", "telnet"]
        print(f"No commands specified, using defaults: {', '.join(forbidden_commands)}")

    # Define patterns that exempt a line from keyword checking
    # This allows mentions of commands in reasoning steps or command output logs
    exempt_patterns = [
        r"^\s*└\s*action.*",  # Reasoning step line
        r"^\s*■.*?(?:failed|executing).*",  # Command execution line
        r"command execution failed",  # Error message line
        r"UPDATE AVAILABLE",  # CLI update notification
        r"^\s*◇\s*",  # Agent output markers
    ]

    # Read from stdin
    input_text = sys.stdin.read()

    # Test for forbidden keywords
    result = test_forbidden_keywords(input_text, forbidden_commands, exempt_patterns)

    # Exit with appropriate status code
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
