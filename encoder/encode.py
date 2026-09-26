#!/usr/bin/env python3
"""
BananaLLM bootstrap encoder.
Encodes plain text into an nlm-v1 .nlm file using a given dictionary.
This is scaffolding only, not the final native BananaLLM toolchain.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from banana_common import load_dictionary, build_reverse_dictionary  # noqa: E402


def encode_text(text, dictionary):
    reverse = build_reverse_dictionary(dictionary)
    tokens = []
    for i, ch in enumerate(text):
        if ch == " ":
            tokens.append("=")
        elif ch in reverse:
            tokens.append(reverse[ch])
        else:
            raise ValueError(
                f"Character {ch!r} at position {i} has no token in this dictionary"
            )
    return tokens


def build_nlm(tokens, dictionary_name):
    lines = [
        "format: nlm-v1",
        f"dictionary: {dictionary_name}",
        "type: text",
        "data {",
        ",".join(tokens),
        "}",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Encode text into a BananaLLM nlm-v1 file"
    )
    parser.add_argument("text", help="Text to encode")
    parser.add_argument("-o", "--output", help="Output .nlm file path")
    parser.add_argument(
        "--dictionary", default="english-basic-v1", help="Dictionary name"
    )
    parser.add_argument(
        "--dictionaries-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "dictionaries"),
        help="Directory containing .map dictionary files",
    )
    args = parser.parse_args()

    dict_path = os.path.join(args.dictionaries_dir, f"{args.dictionary}.map")
    dictionary = load_dictionary(dict_path)

    try:
        tokens = encode_text(args.text, dictionary)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_text = build_nlm(tokens, args.dictionary)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Wrote {args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
