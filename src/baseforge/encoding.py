"""Encoding and decoding operations for various formats."""

import base64
import html
import re
import urllib.parse

# Base encoding/decoding


def base64_encode(data: str, url_safe: bool = False) -> str:
    """Encode string to Base64."""
    raw = data.encode("utf-8")
    if url_safe:
        return base64.urlsafe_b64encode(raw).decode("ascii")
    return base64.b64encode(raw).decode("ascii")


def base64_decode(encoded: str, url_safe: bool = False) -> str:
    """Decode Base64 string."""
    # Add padding if needed
    padded = encoded + "=" * (-len(encoded) % 4)
    if url_safe:
        return base64.urlsafe_b64decode(padded).decode("utf-8")
    return base64.b64decode(padded).decode("utf-8")


def base32_encode(data: str) -> str:
    """Encode string to Base32."""
    return base64.b32encode(data.encode("utf-8")).decode("ascii")


def base32_decode(encoded: str) -> str:
    """Decode Base32 string."""
    padded = encoded + "=" * (-len(encoded) % 8)
    return base64.b32decode(padded).decode("utf-8")


def base16_encode(data: str) -> str:
    """Encode string to Base16 (hex)."""
    return base64.b16encode(data.encode("utf-8")).decode("ascii")


def base16_decode(encoded: str) -> str:
    """Decode Base16 (hex) string."""
    padded = encoded + "=" * (-len(encoded) % 2)
    return base64.b16decode(padded.upper()).decode("utf-8")


def base85_encode(data: str) -> str:
    """Encode string to Base85 (ASCII85)."""
    return base64.b85encode(data.encode("utf-8")).decode("ascii")


def base85_decode(encoded: str) -> str:
    """Decode Base85 (ASCII85) string."""
    return base64.b85decode(encoded.encode("ascii")).decode("utf-8")


def hex_encode(data: str) -> str:
    """Encode string to hexadecimal."""
    return data.encode("utf-8").hex()


def hex_decode(encoded: str) -> str:
    """Decode hexadecimal string."""
    # Remove any whitespace or 0x prefix
    cleaned = re.sub(r"\s+", "", encoded).replace("0x", "").replace("0X", "")
    return bytes.fromhex(cleaned).decode("utf-8")


def binary_encode(data: str) -> str:
    """Encode string to binary representation."""
    return " ".join(format(byte, "08b") for byte in data.encode("utf-8"))


def binary_decode(encoded: str) -> str:
    """Decode binary representation."""
    # Split by spaces or newlines, filter empty strings
    parts = [p for p in re.split(r"\s+", encoded.strip()) if p]
    return bytes(int(p, 2) for p in parts).decode("utf-8")


# URL encoding


def url_encode(data: str, safe: str = "") -> str:
    """URL-encode a string."""
    return urllib.parse.quote(data, safe=safe)


def url_decode(encoded: str) -> str:
    """URL-decode a string."""
    return urllib.parse.unquote(encoded)


def url_encode_plus(data: str) -> str:
    """URL-encode using + for spaces (form encoding)."""
    return urllib.parse.quote_plus(data)


def url_decode_plus(encoded: str) -> str:
    """URL-decode + encoded strings."""
    return urllib.parse.unquote_plus(encoded)


# HTML encoding


def html_encode(data: str) -> str:
    """Encode special characters to HTML entities."""
    return html.escape(data)


def html_decode(encoded: str) -> str:
    """Decode HTML entities."""
    return html.unescape(encoded)


# Unicode encoding


def unicode_escape_encode(data: str) -> str:
    """Encode string to Unicode escape sequences."""
    return data.encode("unicode_escape").decode("ascii")


def unicode_escape_decode(encoded: str) -> str:
    """Decode Unicode escape sequences."""
    # Handle both \uXXXX and \UXXXXXXXX formats
    return encoded.encode("utf-8").decode("unicode_escape")


# Punycode (Internationalized Domain Names)


def punycode_encode(data: str) -> str:
    """Encode domain name to Punycode (ACE)."""
    return data.encode("punycode").decode("ascii")


def punycode_decode(encoded: str) -> str:
    """Decode Punycode domain name."""
    return encoded.encode("ascii").decode("punycode")


# Number base conversions


def to_decimal(value: str, base: int) -> int:
    """Convert a number string from given base to decimal."""
    return int(value, base)


def from_decimal(value: int, base: int) -> str:
    """Convert decimal number to given base string."""
    if base == 2:
        return bin(value)[2:]
    elif base == 8:
        return oct(value)[2:]
    elif base == 16:
        return hex(value)[2:].upper()
    elif base == 10:
        return str(value)
    else:
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if value == 0:
            return "0"
        result = ""
        while value > 0:
            result = digits[value % base] + result
            value //= base
        return result


# Hex dump


def hex_dump(data: str, bytes_per_line: int = 16) -> str:
    """Create a hex dump representation of data."""
    raw = data.encode("utf-8")
    lines = []
    for i in range(0, len(raw), bytes_per_line):
        chunk = raw[i : i + bytes_per_line]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hex_part:<{bytes_per_line * 3 - 1}}  |{ascii_part}|")
    return "\n".join(lines)


# Data format detection


def detect_encoding(data: str) -> dict:
    """Detect possible encoding of input data."""
    results = {
        "raw": True,
        "base64": False,
        "base32": False,
        "hex": False,
        "url_encoded": False,
        "html_entities": False,
        "unicode_escape": False,
        "binary": False,
    }

    # Check base64
    b64_pattern = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")
    if b64_pattern.match(data) and len(data) % 4 == 0 and len(data) > 0:
        try:
            base64.b64decode(data + "=" * (-len(data) % 4))
            results["base64"] = True
        except Exception:
            pass

    # Check base32
    b32_pattern = re.compile(r"^[A-Z2-7]+=*$")
    if b32_pattern.match(data) and len(data) > 0:
        try:
            padded = data + "=" * (-len(data) % 8)
            base64.b32decode(padded)
            results["base32"] = True
        except Exception:
            pass

    # Check hex
    hex_pattern = re.compile(r"^(0x)?[0-9A-Fa-f]+$")
    if hex_pattern.match(data) and len(data) > 0:
        results["hex"] = True

    # Check URL encoding
    if "%" in data:
        try:
            decoded = urllib.parse.unquote(data)
            if decoded != data:
                results["url_encoded"] = True
        except Exception:
            pass

    # Check HTML entities
    if "&" in data and ";" in data:
        decoded = html.unescape(data)
        if decoded != data:
            results["html_entities"] = True

    # Check unicode escape
    if "\\u" in data or "\\U" in data:
        try:
            data.encode("utf-8").decode("unicode_escape")
            results["unicode_escape"] = True
        except Exception:
            pass

    # Check binary
    binary_pattern = re.compile(r"^[01 ]+$")
    if binary_pattern.match(data) and " " in data:
        parts = data.split()
        if all(len(p) == 8 and all(c in "01" for c in p) for p in parts):
            results["binary"] = True

    return results
