# BaseForge

Comprehensive Encoding, Decoding & Crypto Utility CLI

A unified command-line tool for all your encoding, decoding, hashing, JWT, UUID, timestamp, and cipher operations. No more juggling between `base64`, `openssl`, `uuidgen`, and writing Python scripts for simple conversions.

## Features

- **Encoding/Decoding**: Base64, Base32, Base16, Base85, Hex, Binary, URL, HTML entities, Unicode escapes, Punycode
- **JWT Operations**: Decode, encode, validate, and inspect JWT tokens
- **UUID Operations**: Generate (v1, v3, v4, v5), validate, and analyze UUIDs
- **Timestamps**: Parse, convert, and analyze timestamps in multiple formats
- **Hashing**: MD5, SHA-1, SHA-256, SHA-512, SHA-3, BLAKE2, HMAC
- **Ciphers**: ROT13, Caesar, Atbash, Vigenere with frequency analysis
- **Number Bases**: Convert between decimal, hex, octal, binary, and arbitrary bases
- **Hex Dump**: Classic hex dump with ASCII representation
- **Encoding Detection**: Auto-detect encoding of input data

## Installation

```bash
pip install baseforge
```

Or from source:

```bash
git clone https://github.com/EdgarOrtegaRamirez/baseforge
cd baseforge
pip install -e .
```

## Quick Start

### Encoding/Decoding

```bash
# Base64 encode/decode
baseforge encode b64 "Hello, World!"
baseforge decode b64 "SGVsbG8sIFdvcmxkIQ=="

# URL encode/decode
baseforge encode url "key=value&foo=bar baz"
baseforge decode url "key%3Dvalue%26foo%3Dbar%20baz"

# Hex encode/decode
baseforge encode hex "Hello"
baseforge decode hex "48656c6c6f"
```

### JWT Operations

```bash
# Decode a JWT token (without verification)
baseforge jwt decode eyJhbGciOiJIUzI1NiJ9...

# Encode a JWT token
baseforge jwt encode --payload '{"sub":"user123"}' --secret "my-secret"

# Validate a JWT token
baseforge jwt validate eyJhbGci... --secret "my-secret"

# Get detailed JWT info
baseforge jwt info eyJhbGci...
```

### UUID Operations

```bash
# Generate UUID v4 (random)
baseforge uuid generate

# Generate 5 UUIDs
baseforge uuid generate --count 5

# Generate UUID v5 (deterministic)
baseforge uuid generate --version 5 --name "example.com"

# Validate a UUID
baseforge uuid validate "550e8400-e29b-41d4-a716-446655440000"
```

### Timestamp Operations

```bash
# Show current timestamp
baseforge timestamp now

# Convert Unix timestamp to ISO 8601
baseforge timestamp convert 1609459200

# Get detailed timestamp info
baseforge timestamp info 1609459200
```

### Hashing

```bash
# Compute SHA-256 hash
baseforge hash sha256 "my secret data"

# Compute all common hashes
baseforge hash all "test data"

# Compute HMAC
baseforge hmac sha256 "data" --key "secret"

# Verify HMAC
baseforge hmac sha256 "data" --key "secret" --verify "expected_hmac"
```

### Ciphers

```bash
# ROT13
baseforge cipher rot13 "Hello World"

# Caesar cipher
baseforge cipher caesar "Attack at dawn" --shift 5
baseforge cipher caesar "Fyyfhpj fy ifbs" --shift 5 --decrypt

# Analyze text for cipher patterns
baseforge cipher analyze "encrypted text"
```

### Number Base Conversion

```bash
# Hex to decimal
baseforge base ff --from-base 16 --to-base 10

# Decimal to binary
baseforge base 255 --from-base 10 --to-base 2

# Binary to hex
baseforge base "10101010" --from-base 2 --to-base 16
```

### Encoding Detection

```bash
# Detect encoding of input
baseforge detect "SGVsbG8="
baseforge detect "48656c6c6f"
baseforge detect "hello%20world"
```

### Hex Dump

```bash
# Create hex dump
baseforge hexdump "Hello, World!"
```

## Supported Encodings

| Format | Encode | Decode | Description |
|--------|--------|--------|-------------|
| `b64` | ✓ | ✓ | Base64 (standard) |
| `b64url` | ✓ | ✓ | Base64 URL-safe |
| `b32` | ✓ | ✓ | Base32 |
| `b16` | ✓ | ✓ | Base16 (hex) |
| `b85` | ✓ | ✓ | Base85 (ASCII85) |
| `hex` | ✓ | ✓ | Hexadecimal |
| `binary` | ✓ | ✓ | Binary representation |
| `url` | ✓ | ✓ | URL encoding |
| `urlplus` | ✓ | ✓ | URL encoding (+ for spaces) |
| `html` | ✓ | ✓ | HTML entities |
| `unicode` | ✓ | ✓ | Unicode escape sequences |

## Hash Algorithms

MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SHA3-224, SHA3-256, SHA3-384, SHA3-512, BLAKE2b, BLAKE2s

## JSON Output

Use `--json` flag for machine-readable output:

```bash
baseforge --json jwt decode eyJhbGci...
baseforge --json uuid validate "550e8400-..."
```

## Architecture

```
src/baseforge/
├── __init__.py      # Package metadata
├── cli.py           # CLI entry point with argparse
├── encoding.py      # Encoding/decoding operations
├── jwt_ops.py       # JWT decode/encode/validate
├── uuid_ops.py      # UUID generation/validation
├── timestamp.py     # Timestamp parsing/conversion
├── hashing.py       # Hash and HMAC computation
└── cipher.py        # Classical cipher operations
```

## Security Notes

- JWT validation uses constant-time comparison to prevent timing attacks
- No secrets are logged or stored by the tool
- All operations are performed locally — no network requests
- HMAC verification uses `hmac.compare_digest()` for secure comparison

## License

MIT License — see [LICENSE](LICENSE) for details.
