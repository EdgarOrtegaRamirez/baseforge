"""BaseForge CLI - Comprehensive Encoding, Decoding & Crypto Utility."""

import argparse
import json
import sys

from . import __version__, cipher, encoding, hashing, jwt_ops, timestamp, uuid_ops


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="baseforge",
        description="BaseForge: Comprehensive Encoding, Decoding & Crypto Utility CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  baseforge encode b64 "Hello World"
  baseforge decode b64 "SGVsbG8gV29ybGQ="
  baseforge jwt decode eyJhbGciOiJIUzI1NiIs...
  baseforge uuid generate --count 5
  baseforge timestamp now
  baseforge hash sha256 "my secret"
  baseforge cipher rot13 "Hello World"
  baseforge detect "SGVsbG8="
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Encode command
    encode_parser = subparsers.add_parser("encode", help="Encode data")
    encode_parser.add_argument(
        "format",
        choices=[
            "b64",
            "b64url",
            "b32",
            "b16",
            "b85",
            "hex",
            "binary",
            "url",
            "urlplus",
            "html",
            "unicode",
        ],
        help="Encoding format",
    )
    encode_parser.add_argument("data", help="Data to encode (or - for stdin)")
    encode_parser.add_argument("--safe", default="", help="URL-safe characters")

    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Decode data")
    decode_parser.add_argument(
        "format",
        choices=[
            "b64",
            "b64url",
            "b32",
            "b16",
            "b85",
            "hex",
            "binary",
            "url",
            "urlplus",
            "html",
            "unicode",
        ],
        help="Decoding format",
    )
    decode_parser.add_argument("data", help="Data to decode (or - for stdin)")

    # JWT command
    jwt_parser = subparsers.add_parser("jwt", help="JWT operations")
    jwt_sub = jwt_parser.add_subparsers(dest="jwt_action", help="JWT action")

    jwt_decode = jwt_sub.add_parser("decode", help="Decode JWT token")
    jwt_decode.add_argument("token", help="JWT token")
    jwt_decode.add_argument("--verify", action="store_true", help="Verify signature")
    jwt_decode.add_argument("--secret", help="Secret key for verification")

    jwt_encode = jwt_sub.add_parser("encode", help="Encode JWT token")
    jwt_encode.add_argument("--payload", required=True, help="JSON payload string")
    jwt_encode.add_argument("--secret", required=True, help="Signing secret")
    jwt_encode.add_argument("--algorithm", default="HS256", help="Signing algorithm")

    jwt_validate = jwt_sub.add_parser("validate", help="Validate JWT token")
    jwt_validate.add_argument("token", help="JWT token")
    jwt_validate.add_argument("--secret", required=True, help="Secret key")

    jwt_info_cmd = jwt_sub.add_parser("info", help="Get JWT info")
    jwt_info_cmd.add_argument("token", help="JWT token")

    # UUID command
    uuid_parser = subparsers.add_parser("uuid", help="UUID operations")
    uuid_sub = uuid_parser.add_subparsers(dest="uuid_action", help="UUID action")

    uuid_gen = uuid_sub.add_parser("generate", help="Generate UUIDs")
    uuid_gen.add_argument(
        "--version", "-v", type=int, default=4, choices=[1, 3, 4, 5], help="UUID version"
    )
    uuid_gen.add_argument("--count", "-n", type=int, default=1, help="Number of UUIDs")
    uuid_gen.add_argument("--name", help="Name for v3/v5 UUIDs")
    uuid_gen.add_argument("--namespace", help="Namespace UUID for v3/v5")

    uuid_validate = uuid_sub.add_parser("validate", help="Validate UUID")
    uuid_validate.add_argument("uuid", help="UUID to validate")

    uuid_info_cmd = uuid_sub.add_parser("info", help="Get UUID info")
    uuid_info_cmd.add_argument("uuid", help="UUID to analyze")

    # Timestamp command
    ts_parser = subparsers.add_parser("timestamp", help="Timestamp operations")
    ts_sub = ts_parser.add_subparsers(dest="ts_action", help="Timestamp action")

    ts_now = ts_sub.add_parser("now", help="Show current timestamp")
    ts_now.add_argument("--format", "-f", default="iso8601", help="Output format")

    ts_convert = ts_sub.add_parser("convert", help="Convert timestamp")
    ts_convert.add_argument("value", help="Timestamp value")
    ts_convert.add_argument("--to", "-t", default="iso8601", dest="to_format", help="Target format")

    ts_info_cmd = ts_sub.add_parser("info", help="Get timestamp info")
    ts_info_cmd.add_argument("value", help="Timestamp value")

    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Compute hash")
    hash_parser.add_argument(
        "algorithm",
        choices=[
            "md5",
            "sha1",
            "sha224",
            "sha256",
            "sha384",
            "sha512",
            "sha3-224",
            "sha3-256",
            "sha3-384",
            "sha3-512",
            "blake2b",
            "blake2s",
            "all",
        ],
        help="Hash algorithm",
    )
    hash_parser.add_argument("data", help="Data to hash (or - for stdin)")
    hash_parser.add_argument(
        "--encoding",
        "-e",
        default="hex",
        choices=["hex", "base64", "base64url"],
        help="Output encoding",
    )

    # HMAC command
    hmac_parser = subparsers.add_parser("hmac", help="Compute HMAC")
    hmac_parser.add_argument(
        "algorithm",
        choices=[
            "md5",
            "sha1",
            "sha256",
            "sha384",
            "sha512",
            "sha3-256",
            "sha3-512",
            "blake2b",
            "blake2s",
        ],
        help="Hash algorithm",
    )
    hmac_parser.add_argument("data", help="Data to sign")
    hmac_parser.add_argument("--key", required=True, help="Secret key")
    hmac_parser.add_argument(
        "--encoding",
        "-e",
        default="hex",
        choices=["hex", "base64", "base64url"],
        help="Output encoding",
    )
    hmac_parser.add_argument("--verify", help="Verify HMAC (provide expected value)")

    # Cipher command
    cipher_parser = subparsers.add_parser("cipher", help="Cipher operations")
    cipher_sub = cipher_parser.add_subparsers(dest="cipher_action", help="Cipher action")

    cipher_rot13 = cipher_sub.add_parser("rot13", help="Apply ROT13")
    cipher_rot13.add_argument("data", help="Text to encrypt/decrypt")

    cipher_caesar = cipher_sub.add_parser("caesar", help="Apply Caesar cipher")
    cipher_caesar.add_argument("data", help="Text to encrypt/decrypt")
    cipher_caesar.add_argument("--shift", "-s", type=int, required=True, help="Shift amount")
    cipher_caesar.add_argument(
        "--decrypt", "-d", action="store_true", help="Decrypt instead of encrypt"
    )

    cipher_atbash_cmd = cipher_sub.add_parser("atbash", help="Apply Atbash cipher")
    cipher_atbash_cmd.add_argument("data", help="Text to encrypt/decrypt")

    cipher_vigenere = cipher_sub.add_parser("vigenere", help="Apply Vigenere cipher")
    cipher_vigenere.add_argument("data", help="Text to encrypt/decrypt")
    cipher_vigenere.add_argument("--key", "-k", required=True, help="Encryption key")
    cipher_vigenere.add_argument(
        "--decrypt", "-d", action="store_true", help="Decrypt instead of encrypt"
    )

    cipher_analyze = cipher_sub.add_parser("analyze", help="Analyze text for cipher patterns")
    cipher_analyze.add_argument("data", help="Text to analyze")

    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect encoding of data")
    detect_parser.add_argument("data", help="Data to analyze")

    # Base command
    base_parser = subparsers.add_parser("base", help="Number base conversion")
    base_parser.add_argument("value", help="Number to convert")
    base_parser.add_argument(
        "--from-base", "-f", type=int, required=True, help="Source base (2-36)"
    )
    base_parser.add_argument("--to-base", "-t", type=int, required=True, help="Target base (2-36)")

    # Hexdump command
    hexdump_parser = subparsers.add_parser("hexdump", help="Create hex dump")
    hexdump_parser.add_argument("data", help="Data to dump (or - for stdin)")
    hexdump_parser.add_argument(
        "--bytes-per-line", "-b", type=int, default=16, help="Bytes per line"
    )

    return parser


def read_input(data: str) -> str:
    """Read input from argument or stdin."""
    if data == "-":
        return sys.stdin.read().strip()
    return data


def main(argv: list | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        output = _execute_command(args)
        if args.json:
            print(json.dumps(output, indent=2, default=str))
        else:
            print(output)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _execute_command(args) -> str:
    """Execute a command and return output."""
    if args.command == "encode":
        return _encode(args)
    elif args.command == "decode":
        return _decode(args)
    elif args.command == "jwt":
        return _jwt(args)
    elif args.command == "uuid":
        return _uuid(args)
    elif args.command == "timestamp":
        return _timestamp(args)
    elif args.command == "hash":
        return _hash(args)
    elif args.command == "hmac":
        return _hmac(args)
    elif args.command == "cipher":
        return _cipher(args)
    elif args.command == "detect":
        return _detect(args)
    elif args.command == "base":
        return _base(args)
    elif args.command == "hexdump":
        return _hexdump(args)
    return ""


def _encode(args) -> str:
    """Handle encode command."""
    data = read_input(args.data)
    fmt = args.format

    encoders = {
        "b64": lambda d: encoding.base64_encode(d),
        "b64url": lambda d: encoding.base64_encode(d, url_safe=True),
        "b32": lambda d: encoding.base32_encode(d),
        "b16": lambda d: encoding.base16_encode(d),
        "b85": lambda d: encoding.base85_encode(d),
        "hex": lambda d: encoding.hex_encode(d),
        "binary": lambda d: encoding.binary_encode(d),
        "url": lambda d: encoding.url_encode(d, safe=args.safe),
        "urlplus": lambda d: encoding.url_encode_plus(d),
        "html": lambda d: encoding.html_encode(d),
        "unicode": lambda d: encoding.unicode_escape_encode(d),
    }

    return encoders[fmt](data)


def _decode(args) -> str:
    """Handle decode command."""
    data = read_input(args.data)
    fmt = args.format

    decoders = {
        "b64": lambda d: encoding.base64_decode(d),
        "b64url": lambda d: encoding.base64_decode(d, url_safe=True),
        "b32": lambda d: encoding.base32_decode(d),
        "b16": lambda d: encoding.base16_decode(d),
        "b85": lambda d: encoding.base85_decode(d),
        "hex": lambda d: encoding.hex_decode(d),
        "binary": lambda d: encoding.binary_decode(d),
        "url": lambda d: encoding.url_decode(d),
        "urlplus": lambda d: encoding.url_decode_plus(d),
        "html": lambda d: encoding.html_decode(d),
        "unicode": lambda d: encoding.unicode_escape_decode(d),
    }

    return decoders[fmt](data)


def _jwt(args) -> str:
    """Handle JWT command."""
    if args.jwt_action == "decode":
        result = jwt_ops.decode_jwt(args.token, verify=args.verify, secret=args.secret)
        return json.dumps(result, indent=2, default=str)
    elif args.jwt_action == "encode":
        payload = json.loads(args.payload)
        token = jwt_ops.encode_jwt(payload, args.secret, args.algorithm)
        return token
    elif args.jwt_action == "validate":
        valid = jwt_ops.validate_jwt(args.token, args.secret)
        return "Valid" if valid else "Invalid"
    elif args.jwt_action == "info":
        return jwt_ops.jwt_info(args.token)
    return ""


def _uuid(args) -> str:
    """Handle UUID command."""
    if args.uuid_action == "generate":
        if args.version in (3, 5):
            name = args.name or "item-0"
            namespace = args.namespace or str(uuid_ops.uuid.NAMESPACE_DNS)
            results = []
            for i in range(args.count):
                n = f"{name}-{i}" if args.count > 1 else name
                results.append(uuid_ops.generate_uuid(args.version, name=n, namespace=namespace))
            return "\n".join(results)
        else:
            results = [uuid_ops.generate_uuid(args.version) for _ in range(args.count)]
            return "\n".join(results)
    elif args.uuid_action == "validate":
        result = uuid_ops.validate_uuid(args.uuid)
        return json.dumps(result, indent=2, default=str)
    elif args.uuid_action == "info":
        return uuid_ops.uuid_info(args.uuid)
    return ""


def _timestamp(args) -> str:
    """Handle timestamp command."""
    if args.ts_action == "now":
        return timestamp.format_timestamp(
            __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            args.format,
        )
    elif args.ts_action == "convert":
        return timestamp.convert_timestamp(args.value, args.to_format)
    elif args.ts_action == "info":
        return timestamp.timestamp_info(args.value)
    return ""


def _hash(args) -> str:
    """Handle hash command."""
    data = read_input(args.data)
    if args.algorithm == "all":
        lines = []
        for algo in ["md5", "sha1", "sha256", "sha512", "sha3-256", "blake2b"]:
            h = hashing.compute_hash(data, algo, args.encoding)
            lines.append(f"{algo:>8}: {h}")
        return "\n".join(lines)
    return hashing.compute_hash(data, args.algorithm, args.encoding)


def _hmac(args) -> str:
    """Handle HMAC command."""
    data = read_input(args.data)
    if args.verify:
        valid = hashing.verify_hmac(data, args.key, args.verify, args.algorithm)
        return "Valid" if valid else "Invalid"
    return hashing.compute_hmac(data, args.key, args.algorithm, args.encoding)


def _cipher(args) -> str:
    """Handle cipher command."""
    if args.cipher_action == "rot13":
        return cipher.rot13(args.data)
    elif args.cipher_action == "caesar":
        return cipher.caesar_cipher(args.data, args.shift, args.decrypt)
    elif args.cipher_action == "atbash":
        return cipher.atbash(args.data)
    elif args.cipher_action == "vigenere":
        return cipher.vigenere_cipher(args.data, args.key, args.decrypt)
    elif args.cipher_action == "analyze":
        return cipher.cipher_info(args.data)
    return ""


def _detect(args) -> str:
    """Handle detect command."""
    data = read_input(args.data)
    results = encoding.detect_encoding(data)
    lines = ["Encoding Detection", "=" * 40]
    lines.append(f"Input: {data[:100]}{'...' if len(data) > 100 else ''}")
    lines.append("")
    for enc, detected in results.items():
        if detected:
            lines.append(f"  ✓ {enc}")
    return "\n".join(lines)


def _base(args) -> str:
    """Handle base command."""
    value = args.value
    from_base = args.from_base
    to_base = args.to_base

    # Handle common prefixes
    if value.startswith("0x") or value.startswith("0X"):
        from_base = 16
        value = value[2:]
    elif value.startswith("0b") or value.startswith("0B"):
        from_base = 2
        value = value[2:]
    elif value.startswith("0o") or value.startswith("0O"):
        from_base = 8
        value = value[2:]

    decimal = encoding.to_decimal(value, from_base)
    return encoding.from_decimal(decimal, to_base)


def _hexdump(args) -> str:
    """Handle hexdump command."""
    data = read_input(args.data)
    return encoding.hex_dump(data, args.bytes_per_line)
