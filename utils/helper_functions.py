import re 


def parse_input(input):
    """
    Splits the user's input (comma, space, newline) into a list of unique, non-empty strings.
        input: str: The user's input eg. gene names, GO terms...
        tokens: list: A list of unique, non-empty strings.
    """
    if not input.strip():
        return []
    # Replace commas/newlines with spaces
    cleaned = input.replace("\n", ",")
    # Split on comma
    tokens = list(set([t.strip() for t in cleaned.split(",") if t.strip()]))
    # Return unique tokens
    return tokens

