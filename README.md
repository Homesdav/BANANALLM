# BananaLLM

BananaLLM is a structured, AI oriented text format. Files use the `.nlm`
extension and represent text as a sequence of compact numeric tokens, so
AI systems can process the data consistently and deterministically.

BananaLLM is **not**:

- A web framework
- A general purpose programming language
- A replacement for an LLM

It is a data format. A format alone does not make an AI smarter or
automatically easier to train. What BananaLLM provides is consistency,
deterministic token mapping, compact storage, validation, and
reproducible decoding.

Full details are in [`specification/nlm-v1.md`](specification/nlm-v1.md).

## Example

`examples/message.nlm`:

```
format: nlm-v1
dictionary: english-basic-v1
type: text
data {
1,2,=,3
}
```

With dictionary `1=A, 2=B, 3=C, ==space`, this decodes to `"AB C"`.

## Status

This repository currently ships a **bootstrap** toolchain written in
Python (`encoder/`, `decoder/`, `validator/`, `common/`). It exists to
prove the format out and is not the final implementation. The long term
goal is a native BananaLLM toolchain that reads, validates, encodes, and
decodes `.nlm` files without depending on Python, JavaScript, or any
other host language.

## Usage

From the repository root:

```
./bin/nlm encode "HELLO WORLD" -o examples/hello.nlm
./bin/nlm decode examples/hello.nlm
./bin/nlm validate examples/hello.nlm
./bin/nlm dev examples/hello.nlm
```

`nlm dev <file>` watches a `.nlm` file and reprints its validation status
and decoded text every time the file is saved -- a fast feedback loop
while hand editing a file, similar in spirit to a dev-server reload.
It only prints to the terminal; it does not serve anything over HTTP,
so BananaLLM stays a data format, not a web framework.

Requires Python 3. No third-party packages are needed.

## Running the tests

```
python3 -m unittest discover -s tests -v
```

## Repository layout

```
bananallm/
├── README.md
├── LICENSE
├── specification/
│   └── nlm-v1.md          nlm-v1 format specification
├── dictionaries/
│   └── english-basic-v1.map   token -> character mapping
├── examples/
│   ├── message.nlm         the canonical spec example
│   └── hello.nlm           produced by the encoder
├── common/
│   └── banana_common.py    shared parsing/loading helpers
├── encoder/
│   └── encode.py           text -> .nlm
├── decoder/
│   └── decode.py           .nlm -> text
├── validator/
│   └── validate.py         structural + token validation
├── dev/
│   └── dev.py               watch a file, live-reprint decode + validate
├── bin/
│   └── nlm                  CLI wrapper (encode/decode/validate/dev)
└── tests/
    └── test_nlm.py          round-trip and validation tests
```

## Design principles

- Simple, deterministic, text based, easy to validate.
- Commas separate tokens; curly brackets define the data block.
- `=` always means one space, independent of dictionary.
- Every token has exactly one documented meaning.
- Unknown tokens are rejected with a clear, specific error, never
  silently ignored.
- Dictionaries are versioned and immutable; changes require a new
  dictionary version.

## Character mode vs. word mode

- **Character mode**: `1=A`, `2=B`, `3=C`. Small dictionary, more tokens
  per word.
- **Word mode**: `101=hello`, `102=world`, `103=space`. Fewer tokens for
  common text, larger dictionary, less flexible for arbitrary text.

Both should be compared on file size, token count, encoding speed,
decoding speed, readability, reversibility, and compatibility with AI
dataset pipelines before picking one for a given use case.

## Contributing

See `specification/nlm-v1.md` before proposing changes. Any change to an
existing dictionary's meaning must ship as a new dictionary version, not
an edit to an existing one.

## License

MIT. See [`LICENSE`](LICENSE).
