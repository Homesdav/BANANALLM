"""
Shared helpers for the BananaLLM bootstrap tools (encoder, decoder,
validator). This is scaffolding only: the long term goal is a native
BananaLLM toolchain that does not depend on Python.
"""

SPECIAL_VALUES = {
    "<NEWLINE>": "\n",
}

# Used when a .nlm file omits the header entirely (shorthand form).
DEFAULT_HEADER = {
    "format": "nlm-v1",
    "dictionary": "english-basic-v1",
    "type": "text",
}


def load_dictionary(path):
    """Load a .map dictionary file into a {token: value} dict."""
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Malformed dictionary line {line_number}: {raw_line!r}"
                )
            token, value = line.split("=", 1)
            token = token.strip()
            value = value.strip()
            if not token.isdigit():
                raise ValueError(
                    f"Malformed dictionary line {line_number}: "
                    f"token {token!r} is not a positive integer"
                )
            value = SPECIAL_VALUES.get(value, value)
            mapping[token] = value
    return mapping


def build_reverse_dictionary(dictionary):
    """Build a {value: token} map, first definition wins on duplicates."""
    reverse = {}
    for token, value in dictionary.items():
        if value not in reverse:
            reverse[value] = token
    return reverse


def parse_header(header_lines):
    """Parse 'key: value' lines into a dict and check required fields."""
    header = {}
    for line in header_lines:
        if ":" not in line:
            raise ValueError(f"Malformed header line: {line!r}")
        key, value = line.split(":", 1)
        header[key.strip()] = value.strip()

    for required_key in ("format", "dictionary", "type"):
        if required_key not in header:
            raise ValueError(f"Missing header field '{required_key}'")

    return header


def parse_nlm_file(path):
    """
    Parse a .nlm file into (header_dict, token_list).
    Raises ValueError with a clear message on structural problems.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "{" not in content:
        raise ValueError("Data block not found (missing '{')")
    if "}" not in content:
        raise ValueError("Data block not closed (missing '}')")

    header_part, rest = content.split("{", 1)
    data_part, _ = rest.split("}", 1)

    header_lines = [
        line.strip() for line in header_part.strip().splitlines() if line.strip()
    ]
    # Drop a trailing "data {" or "filename.nlm {" style line if present,
    # e.g. a bare label on its own line right before the '{' we already
    # split on. That label is not a header field.
    if header_lines and ":" not in header_lines[-1]:
        header_lines = header_lines[:-1]

    if header_lines:
        header = parse_header(header_lines)
    else:
        # Shorthand form: no header at all, e.g.
        #   message.nlm {
        #       1,2,3
        #   }
        # Falls back to the nlm-v1 defaults.
        header = dict(DEFAULT_HEADER)

    raw_tokens = data_part.strip().splitlines()
    raw_tokens = ",".join(raw_tokens).split(",")
    tokens = []
    for i, raw_token in enumerate(raw_tokens):
        token = raw_token.strip()
        if token == "":
            raise ValueError(f"Empty token at position {i}")
        tokens.append(token)

    return header, tokens
