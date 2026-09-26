"""
Tests for the BananaLLM bootstrap toolchain.
Run with: python3 -m unittest discover -s tests
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "common"))
sys.path.insert(0, os.path.join(ROOT, "encoder"))
sys.path.insert(0, os.path.join(ROOT, "decoder"))
sys.path.insert(0, os.path.join(ROOT, "validator"))

from banana_common import load_dictionary, parse_nlm_file  # noqa: E402
from encode import encode_text, build_nlm  # noqa: E402
from decode import decode_tokens  # noqa: E402
from validate import validate_file  # noqa: E402

DICT_PATH = os.path.join(ROOT, "dictionaries", "english-basic-v1.map")
DICT_DIR = os.path.join(ROOT, "dictionaries")


class TestRoundTrip(unittest.TestCase):
    def setUp(self):
        self.dictionary = load_dictionary(DICT_PATH)

    def test_spec_example_decodes_correctly(self):
        tokens = ["1", "2", "=", "3"]
        self.assertEqual(decode_tokens(tokens, self.dictionary), "AB C")

    def test_round_trip_hello_world(self):
        original = "HELLO WORLD"
        tokens = encode_text(original, self.dictionary)
        decoded = decode_tokens(tokens, self.dictionary)
        self.assertEqual(decoded, original)

    def test_round_trip_mixed_case_and_punctuation(self):
        original = "Hello, World!"
        tokens = encode_text(original, self.dictionary)
        decoded = decode_tokens(tokens, self.dictionary)
        self.assertEqual(decoded, original)

    def test_unknown_character_raises(self):
        with self.assertRaises(ValueError):
            encode_text("50% off", self.dictionary)

    def test_unknown_token_raises_on_decode(self):
        with self.assertRaises(ValueError):
            decode_tokens(["1", "999"], self.dictionary)


class TestParsing(unittest.TestCase):
    def test_parse_nlm_file(self):
        path = os.path.join(ROOT, "examples", "message.nlm")
        header, tokens = parse_nlm_file(path)
        self.assertEqual(header["format"], "nlm-v1")
        self.assertEqual(header["dictionary"], "english-basic-v1")
        self.assertEqual(header["type"], "text")
        self.assertEqual(tokens, ["1", "2", "=", "3"])

    def test_build_nlm_round_trips_through_parse(self):
        text = build_nlm(["1", "2", "=", "3"], "english-basic-v1")
        tmp_path = os.path.join(ROOT, "examples", "_tmp_test.nlm")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
        try:
            header, tokens = parse_nlm_file(tmp_path)
            self.assertEqual(header["dictionary"], "english-basic-v1")
            self.assertEqual(tokens, ["1", "2", "=", "3"])
        finally:
            os.remove(tmp_path)


class TestShorthand(unittest.TestCase):
    def test_shorthand_file_parses_with_default_header(self):
        path = os.path.join(ROOT, "examples", "message-shorthand.nlm")
        header, tokens = parse_nlm_file(path)
        self.assertEqual(header["format"], "nlm-v1")
        self.assertEqual(header["dictionary"], "english-basic-v1")
        self.assertEqual(header["type"], "text")
        self.assertEqual(tokens, ["1", "2", "3"])

    def test_shorthand_file_decodes_and_validates(self):
        path = os.path.join(ROOT, "examples", "message-shorthand.nlm")
        errors = validate_file(path, DICT_DIR)
        self.assertEqual(errors, [])
        dictionary = load_dictionary(DICT_PATH)
        _, tokens = parse_nlm_file(path)
        self.assertEqual(decode_tokens(tokens, dictionary), "ABC")


class TestValidation(unittest.TestCase):
    def test_valid_file_passes(self):
        path = os.path.join(ROOT, "examples", "message.nlm")
        errors = validate_file(path, DICT_DIR)
        self.assertEqual(errors, [])

    def test_unknown_token_is_reported(self):
        tmp_path = os.path.join(ROOT, "examples", "_tmp_invalid.nlm")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(
                "format: nlm-v1\n"
                "dictionary: english-basic-v1\n"
                "type: text\n"
                "data {\n"
                "1,2,999,=,3\n"
                "}\n"
            )
        try:
            errors = validate_file(tmp_path, DICT_DIR)
            self.assertEqual(len(errors), 1)
            self.assertIn("999", errors[0])
        finally:
            os.remove(tmp_path)

    def test_missing_header_field_is_reported(self):
        tmp_path = os.path.join(ROOT, "examples", "_tmp_missing_header.nlm")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(
                "format: nlm-v1\n"
                "dictionary: english-basic-v1\n"
                "data {\n"
                "1,2,=,3\n"
                "}\n"
            )
        try:
            errors = validate_file(tmp_path, DICT_DIR)
            self.assertTrue(any("type" in e for e in errors))
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
