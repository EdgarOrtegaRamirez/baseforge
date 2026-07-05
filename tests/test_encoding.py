"""Tests for encoding module."""

from baseforge.encoding import (
    base16_decode,
    base16_encode,
    base32_decode,
    base32_encode,
    base64_decode,
    base64_encode,
    base85_decode,
    base85_encode,
    binary_decode,
    binary_encode,
    detect_encoding,
    from_decimal,
    hex_decode,
    hex_dump,
    hex_encode,
    html_decode,
    html_encode,
    punycode_decode,
    punycode_encode,
    to_decimal,
    unicode_escape_decode,
    unicode_escape_encode,
    url_decode,
    url_decode_plus,
    url_encode,
    url_encode_plus,
)


class TestBase64:
    def test_encode(self):
        assert base64_encode("Hello") == "SGVsbG8="

    def test_decode(self):
        assert base64_decode("SGVsbG8=") == "Hello"

    def test_roundtrip(self):
        data = "Hello, World! 🌍"
        assert base64_decode(base64_encode(data)) == data

    def test_url_safe(self):
        encoded = base64_encode("test>data?", url_safe=True)
        assert "+" not in encoded
        assert "/" not in encoded
        assert base64_decode(encoded, url_safe=True) == "test>data?"

    def test_empty(self):
        assert base64_encode("") == ""
        assert base64_decode("") == ""

    def test_unicode(self):
        data = "日本語テスト"
        encoded = base64_encode(data)
        assert base64_decode(encoded) == data

    def test_padding_handling(self):
        # Without padding should still work
        assert base64_decode("SGVsbG8") == "Hello"


class TestBase32:
    def test_encode(self):
        assert base32_encode("Hello") == "JBSWY3DP"

    def test_decode(self):
        assert base32_decode("JBSWY3DP") == "Hello"

    def test_roundtrip(self):
        data = "Test data 123"
        assert base32_decode(base32_encode(data)) == data

    def test_empty(self):
        assert base32_encode("") == ""
        assert base32_decode("") == ""


class TestBase16:
    def test_encode(self):
        assert base16_encode("Hello") == "48656C6C6F"

    def test_decode(self):
        assert base16_decode("48656C6C6F") == "Hello"

    def test_roundtrip(self):
        data = "Hello World"
        assert base16_decode(base16_encode(data)) == data


class TestBase85:
    def test_encode(self):
        encoded = base85_encode("Hello")
        assert isinstance(encoded, str)
        assert len(encoded) > 0

    def test_decode(self):
        encoded = base85_encode("Hello")
        assert base85_decode(encoded) == "Hello"

    def test_roundtrip(self):
        data = "Base85 encoding test"
        assert base85_decode(base85_encode(data)) == data


class TestHex:
    def test_encode(self):
        assert hex_encode("Hello") == "48656c6c6f"

    def test_decode(self):
        assert hex_decode("48656c6c6f") == "Hello"

    def test_roundtrip(self):
        data = "Hex test 🔤"
        assert hex_decode(hex_encode(data)) == data

    def test_with_prefix(self):
        assert hex_decode("0x48656c6c6f") == "Hello"

    def test_with_spaces(self):
        assert hex_decode("48 65 6c 6c 6f") == "Hello"


class TestBinary:
    def test_encode(self):
        result = binary_encode("Hi")
        assert all(c in "01 " for c in result)
        parts = result.split()
        assert len(parts) == 2
        assert len(parts[0]) == 8

    def test_decode(self):
        encoded = "01001000 01101001"
        assert binary_decode(encoded) == "Hi"

    def test_roundtrip(self):
        data = "Binary test"
        assert binary_decode(binary_encode(data)) == data


class TestURLEncoding:
    def test_encode(self):
        assert url_encode("hello world") == "hello%20world"

    def test_decode(self):
        assert url_decode("hello%20world") == "hello world"

    def test_roundtrip(self):
        data = "key=value&foo=bar baz"
        assert url_decode(url_encode(data)) == data

    def test_encode_plus(self):
        assert url_encode_plus("hello world") == "hello+world"

    def test_decode_plus(self):
        assert url_decode_plus("hello+world") == "hello world"

    def test_special_chars(self):
        encoded = url_encode("a=b&c=d")
        assert url_decode(encoded) == "a=b&c=d"


class TestHTMLEncoding:
    def test_encode(self):
        assert html_encode("<div>&\"'") == "&lt;div&gt;&amp;&quot;&#x27;"

    def test_decode(self):
        assert html_decode("&lt;div&gt;") == "<div>"

    def test_roundtrip(self):
        data = '<script>alert("xss")</script>'
        assert html_decode(html_encode(data)) == data


class TestUnicodeEscape:
    def test_encode(self):
        result = unicode_escape_encode("Hello 🌍")
        assert "\\u" in result or "Hello" in result

    def test_decode(self):
        result = unicode_escape_decode("Hello \\u0021")
        assert result == "Hello !"

    def test_roundtrip(self):
        data = "Café résumé"
        encoded = unicode_escape_encode(data)
        decoded = unicode_escape_decode(encoded)
        assert decoded == data


class TestPunycode:
    def test_encode(self):
        encoded = punycode_encode("münchen")
        assert isinstance(encoded, str)

    def test_decode(self):
        encoded = punycode_encode("münchen")
        decoded = punycode_decode(encoded)
        assert decoded == "münchen"

    def test_roundtrip(self):
        data = "café"
        assert punycode_decode(punycode_encode(data)) == data


class TestNumberBase:
    def test_to_decimal_hex(self):
        assert to_decimal("ff", 16) == 255

    def test_to_decimal_bin(self):
        assert to_decimal("1010", 2) == 10

    def test_to_decimal_oct(self):
        assert to_decimal("77", 8) == 63

    def test_from_decimal_hex(self):
        assert from_decimal(255, 16) == "FF"

    def test_from_decimal_bin(self):
        assert from_decimal(10, 2) == "1010"

    def test_from_decimal_oct(self):
        assert from_decimal(63, 8) == "77"

    def test_roundtrip(self):
        for base in [2, 8, 10, 16]:
            for val in [0, 1, 42, 100, 255]:
                assert int(from_decimal(val, base), base) == val


class TestHexDump:
    def test_basic(self):
        result = hex_dump("Hello")
        assert "48 65 6c 6c 6f" in result
        assert "|Hello|" in result

    def test_non_printable(self):
        result = hex_dump("\x00\x01\x02")
        assert "|" in result

    def test_empty(self):
        result = hex_dump("")
        assert result == ""


class TestDetectEncoding:
    def test_base64(self):
        result = detect_encoding("SGVsbG8=")
        assert result["base64"] is True

    def test_hex(self):
        result = detect_encoding("48656c6c6f")
        assert result["hex"] is True

    def test_url_encoded(self):
        result = detect_encoding("hello%20world")
        assert result["url_encoded"] is True

    def test_html_entities(self):
        result = detect_encoding("&lt;div&gt;")
        assert result["html_entities"] is True

    def test_binary(self):
        result = detect_encoding("01001000 01101001")
        assert result["binary"] is True

    def test_unicode_escape(self):
        result = detect_encoding("\\u0048\\u0065\\u006c\\u006c\\u006f")
        assert result["unicode_escape"] is True
