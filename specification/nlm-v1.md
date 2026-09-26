# BananaLLM Specification: nlm-v1

## 1. Overview

BananaLLM is a structured, AI oriented text format. Files use the `.nlm`
extension. The format represents text as a sequence of compact numeric
tokens so that AI systems can process the data in a consistent,
deterministic way.

BananaLLM is **not** a programming language, a web framework, or a
replacement for an LLM. It is a data format. A format alone does not make
an AI smarter or automatically easier to train; the value BananaLLM adds
is consistency, deterministic token mapping, compact storage, validation,
and reproducible decoding.

## 2. File Structure

A valid `.nlm` file has two required sections, in this order:

1. Header
2. Data block

```
format: nlm-v1
dictionary: english-basic-v1
type: text
data {
1,2,=,3
}
```

## 3. Shorthand Form

The header may be omitted entirely. When it is, tools MUST assume the
nlm-v1 defaults: `format: nlm-v1`, `dictionary: english-basic-v1`,
`type: text`. This lets a file be as short as:

```
message.nlm {
    1,2,3
}
```

The line before `{` (e.g. `message.nlm`) is just a label and is not
parsed as a header field. This decodes to `"ABC"` using the default
dictionary. The explicit header form (Section 4) is still required
whenever a file uses a non-default format, dictionary, or type.

## 4. Header

The header has exactly three required fields, one per line, in
`key: value` form:

| Field        | Meaning                                              |
|--------------|-------------------------------------------------------|
| `format`     | Format version, e.g. `nlm-v1`                          |
| `dictionary` | Name of the dictionary used to interpret tokens        |
| `type`       | Content type of the data block, e.g. `text`            |

All three fields are required. Order does not matter, but each field must
appear exactly once.

## 5. Data Block

The data block starts with `data {` and ends with `}`. Inside it, tokens
are separated by commas:

```
data {
1,2,=,3
}
```

Each token is one of:

- The literal `=` character, which always represents one space. This
  meaning is fixed by the core format and does not depend on the
  dictionary.
- A positive integer, whose meaning is looked up in the dictionary named
  in the header.

Whitespace and line breaks around tokens are ignored by the parser; they
exist only to make files easier to read.

## 6. Token Rules

- One token has exactly one documented meaning.
- Tokens are separated only by commas. No other separators are permitted.
- A token may not be redefined within a file.
- Line breaks in the decoded text are represented by a dedicated
  dictionary token (see `english-basic-v1.map`), never by a raw line
  break inside the data block.
- Empty tokens (produced by a stray leading, trailing, or doubled comma)
  are invalid.

## 7. Dictionary System

A dictionary is a named, versioned mapping from tokens to values. It is
stored in a separate `.map` file, for example
`dictionaries/english-basic-v1.map`.

Dictionary file format, one mapping per line:

```
TOKEN=VALUE
```

- `TOKEN` is a positive integer.
- `VALUE` is either a single literal character, or a named symbol written
  in angle brackets for values that are not printable characters (for
  example `<NEWLINE>`).
- Lines beginning with `#` are comments and are ignored.

Dictionaries are versioned and immutable. `english-basic-v1` will never
change meaning after it is published. Any change to the mapping requires
a new dictionary version, e.g. `english-basic-v2`.

### 6.1 Character mode vs. word mode

- **Character mode** maps each token to a single character, e.g.
  `1=A`, `2=B`, `3=C`. This keeps the dictionary small and simple, but
  produces more tokens per word.
- **Word mode** maps each token to a whole word, e.g. `101=hello`,
  `102=world`, `103=space`. This produces fewer tokens for common text,
  at the cost of a much larger dictionary and less flexibility for
  arbitrary text.

Both modes should be evaluated on the same criteria: file size, token
count, encoding speed, decoding speed, readability, reversibility, and
compatibility with AI dataset pipelines. Neither mode is "correct"; the
right choice depends on the data being encoded.

## 8. Validation Rules

A validator MUST check, in order:

1. The header contains exactly the three required fields, each present
   exactly once.
2. `format` is a version the validator supports (`nlm-v1`).
3. `dictionary` names a dictionary file that exists and loads correctly.
4. `type` is a value the validator supports (`text` in v1).
5. A data block is present, opened with `{` and closed with `}`.
6. Every token is either `=` or a positive integer present in the loaded
   dictionary.
7. No token is empty (see Section 5).

## 9. Error Handling

Validation errors must be specific enough to fix the file without
guessing. Examples:

```
Error: missing header field 'type'
Error: dictionary file not found for 'english-basic-v1'
Error: data block not closed (missing '}')
Error: unknown token '999' at position 4 (dictionary: english-basic-v1)
```

A validator should report every error it finds in one pass rather than
stopping at the first one, where practical.

## 10. Versioning

- `format` pins a file to a format version (`nlm-v1`). Future format
  versions (`nlm-v2`, etc.) may add header fields or new block types, but
  a validator must always be able to identify the format version before
  attempting to parse the rest of the file.
- `dictionary` pins a file to one specific, immutable dictionary version.
  A dictionary is never edited in place; a new version is published
  instead.

## 11. Examples

Character mode, decodes to `"AB C"`:

```
format: nlm-v1
dictionary: english-basic-v1
type: text
data {
1,2,=,3
}
```

Character mode, decodes to `"HELLO WORLD"`:

```
format: nlm-v1
dictionary: english-basic-v1
type: text
data {
8,5,12,12,15,=,23,15,18,12,4
}
```

## 12. Testing Strategy

- Round trip tests: encode a known string, decode it back, and confirm
  it matches the original.
- Validator tests: confirm valid files pass, and that each class of
  invalid file (missing header field, unknown token, unclosed data
  block, empty token) is rejected with a clear error.
- Cross mode tests: encode the same sample text in character mode and in
  a word mode dictionary, and compare file size and token count.

## 13. Future Extensions

- An optional metadata block for authorship, timestamps, and source
  information.
- Word-token dictionaries (e.g. `english-words-v1`) for more compact
  encoding of common text.
- Mixed-dictionary files, where individual tokens can be tagged with
  which dictionary they belong to.
- Additional punctuation and symbol coverage in later dictionary
  versions.
