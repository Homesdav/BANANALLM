#!/usr/bin/env python3
"""
BananaLLM bootstrap 'dev' command.
Watches a .nlm file and reprints its validation status and decoded text
every time the file changes, similar in spirit to a dev-server reload
loop -- but this only ever prints to the terminal. It does not serve
anything over HTTP and does not turn BananaLLM into a web framework.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from banana_common import load_dictionary, parse_nlm_file  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "decoder"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validator"))
from decode import decode_tokens  # noqa: E402
from validate import validate_file  # noqa: E402


def render(path, dictionaries_dir):
    print("\n" + "=" * 40)
    print(f"[nlm dev] {path}")

    errors = validate_file(path, dictionaries_dir)
    if errors:
        print("INVALID")
        for e in errors:
            print(f"  Error: {e}")
        return

    header, tokens = parse_nlm_file(path)
    dict_path = os.path.join(dictionaries_dir, f"{header['dictionary']}.map")
    dictionary = load_dictionary(dict_path)
    text = decode_tokens(tokens, dictionary)

    print("VALID")
    print(f"> {text}")


def main():
    parser = argparse.ArgumentParser(
        description="Watch a .nlm file and live-reload its decoded output"
    )
    parser.add_argument("file", help="Path to .nlm file to watch")
    parser.add_argument(
        "--dictionaries-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "dictionaries"),
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.3,
        help="Poll interval in seconds (default: 0.3)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    print(f"[nlm dev] watching {args.file} (Ctrl+C to stop)")
    render(args.file, args.dictionaries_dir)

    last_mtime = os.path.getmtime(args.file)
    try:
        while True:
            time.sleep(args.interval)
            mtime = os.path.getmtime(args.file)
            if mtime != last_mtime:
                last_mtime = mtime
                render(args.file, args.dictionaries_dir)
    except KeyboardInterrupt:
        print("\n[nlm dev] stopped")


if __name__ == "__main__":
    main()
