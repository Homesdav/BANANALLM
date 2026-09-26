#!/usr/bin/env python3
"""
BananaLLM bootstrap validator.
Validates that a .nlm file is well formed nlm-v1 and every token resolves
against its declared dictionary. This is scaffolding only, not the final
native BananaLLM toolchain.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from banana_common import load_dictionary, parse_nlm_file  # noqa: E402

SUPPORTED_FORMATS = {"nlm-v1"}
SUPPORTED_TYPES = {"text"}


def validate_file(path, dictionaries_dir):
    errors = []

    try:
        header, tokens = parse_nlm_file(path)
    except ValueError as e:
        return [str(e)]

    if header.get("format") not in SUPPORTED_FORMATS:
        errors.append(f"Unsupported format '{header.get('format')}'")

    if header.get("type") not in SUPPORTED_TYPES:
        errors.append(f"Unsupported type '{header.get('type')}'")

    dict_name = header.get("dictionary")
    dictionary = {}
    if not dict_name:
        errors.append("Missing header field 'dictionary'")
    else:
        dict_path = os.path.join(dictionaries_dir, f"{dict_name}.map")
        if not os.path.isfile(dict_path):
            errors.append(f"Dictionary file not found for '{dict_name}'")
        else:
            try:
                dictionary = load_dictionary(dict_path)
            except ValueError as e:
                errors.append(f"Could not load dictionary '{dict_name}': {e}")

    if dictionary:
        for i, token in enumerate(tokens):
            if token != "=" and token not in dictionary:
                errors.append(
                    f"unknown token '{token}' at position {i} "
                    f"(dictionary: {dict_name})"
                )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate a BananaLLM nlm-v1 file"
    )
    parser.add_argument("file", help="Path to .nlm file")
    parser.add_argument(
        "--dictionaries-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "dictionaries"),
        help="Directory containing .map dictionary files",
    )
    args = parser.parse_args()

    errors = validate_file(args.file, args.dictionaries_dir)

    if errors:
        print(f"INVALID: {args.file}")
        for e in errors:
            print(f"  Error: {e}")
        sys.exit(1)
    else:
        print(f"VALID: {args.file}")


if __name__ == "__main__":
    main()
