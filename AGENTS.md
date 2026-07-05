# AGENTS.md — Guide for AI Agents

## Project Overview

BaseForge is a comprehensive encoding, decoding, and cryptographic utility CLI tool for Python. It provides a unified interface for:

- **Encoding/Decoding**: Base64, Base32, Base16, Base85, Hex, Binary, URL, HTML, Unicode, Punycode
- **JWT Operations**: Decode, encode, validate, and inspect JSON Web Tokens
- **UUID Operations**: Generate (v1/v3/v4/v5), validate, and analyze UUIDs
- **Timestamps**: Parse, convert, and analyze timestamps in multiple formats
- **Hashing**: MD5, SHA-1/256/512, SHA-3, BLAKE2, HMAC
- **Ciphers**: ROT13, Caesar, Atbash, Vigenere with frequency analysis
- **Number Bases**: Convert between decimal, hex, octal, binary (2-36)
- **Hex Dump**: Classic hex dump with ASCII representation

## Tech Stack

- **Language**: Python 3.10+
- **Build**: Hatchling
- **Testing**: pytest
- **Linting**: ruff
- **CI**: GitHub Actions

## Project Structure

```
src/baseforge/
├── __init__.py      # Package metadata (__version__, __author__)
├── cli.py           # CLI entry point with argparse
├── encoding.py      # All encoding/decoding operations
├── jwt_ops.py       # JWT decode/encode/validate/inspect
├── uuid_ops.py      # UUID generation/validation/analysis
├── timestamp.py     # Timestamp parsing/conversion/formatting
├── hashing.py       # Hash and HMAC computation
└── cipher.py        # Classical cipher operations

tests/
├── test_encoding.py  # Encoding/decoding tests
├── test_jwt.py       # JWT operation tests
├── test_uuid.py      # UUID operation tests
├── test_timestamp.py # Timestamp tests
├── test_hashing.py   # Hashing tests
├── test_cipher.py    # Cipher tests
└── test_cli.py       # CLI integration tests
```

## Development Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest tests/test_encoding.py

# Run with verbose output
pytest -v

# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/
```

## Key Design Decisions

1. **No external dependencies** — Uses only Python stdlib for maximum portability
2. **Pure Python** — Easy to install, no compilation needed
3. **CLI + Library** — Usable both as command-line tool and Python library
4. **Consistent API** — All modules follow similar patterns (encode/decode/info)
5. **Error handling** — Custom exceptions (JWTError) for domain-specific errors

## Testing Approach

- Unit tests for each module (encoding, jwt, uuid, timestamp, hashing, cipher)
- CLI integration tests using the `main()` function
- Roundtrip tests (encode→decode, encrypt→decrypt) for all operations
- Edge case testing (empty input, invalid input, Unicode)
- No external API dependencies in tests

## Common Tasks

### Adding a new encoding format

1. Add functions to `src/baseforge/encoding.py`
2. Add to the `encoders`/`decoders` dict in `cli.py`
3. Update the format choices in the argparse parser
4. Add tests in `tests/test_encoding.py`

### Adding a new cipher

1. Add functions to `src/baseforge/cipher.py`
2. Add subcommand to the cipher subparser in `cli.py`
3. Add tests in `tests/test_cipher.py`

### Adding a new hash algorithm

1. Add to `HASH_ALGORITHMS` dict in `hashing.py`
2. Add to the choices list in `cli.py`
3. Add tests in `tests/test_hashing.py`

## CI/CD

GitHub Actions runs on push to `main`:
- Python 3.10, 3.11, 3.12, 3.13 matrix
- Lint job (ruff check + ruff format)
- Test job (pytest with coverage)
