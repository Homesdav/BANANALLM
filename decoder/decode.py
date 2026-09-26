#!/usr/bin/env python3
"""
BananaLLM bootstrap decoder.
Decodes an nlm-v1 .nlm file back into plain text.
This is scaffolding only, not the final native BananaLLM toolchain.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from banana_common import load_dictionary, parse_nlm_file  # noqa: E402


def decode_tokens(tokens, dictionary):
    result = []
    for i, token in enumerate(tokens):
        if token == "=":
            result.append(" ")
        elif token in dictionary:
            result.append(dictionary[token])
        else:
            raise ValueError(f"Unknown token '{token}' at position {i}")
    return "".join(result)


def main():
    parser = argparse.ArgumentParser(
        description="Decode a BananaLLM nlm-v1 file into text"
    )
    parser.add_argument("file", help="Path to .nlm file")
    parser.add_argument(
        "--dictionaries-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "dictionaries"),
        help="Directory containing .map dictionary files",
    )
    args = parser.parse_args()

    try:
        header, tokens = parse_nlm_file(args.file)
        dict_path = os.path.join(
            args.dictionaries_dir, f"{header['dictionary']}.map"
        )
        dictionary = load_dictionary(dict_path)
        text = decode_tokens(tokens, dictionary)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(text)


if __name__ == "__main__":
    main()
