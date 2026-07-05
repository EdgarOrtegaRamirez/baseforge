"""Tests for CLI module."""

import json

import pytest

from baseforge.cli import main


class TestCLI:
    def test_help(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_version(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_no_command(self):
        result = main([])
        assert result == 1


class TestEncodeCommand:
    def test_base64(self, capsys):
        result = main(["encode", "b64", "Hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert "SGVsbG8=" in captured.out

    def test_hex(self, capsys):
        result = main(["encode", "hex", "Hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert "48656c6c6f" in captured.out

    def test_url(self, capsys):
        result = main(["encode", "url", "hello world"])
        assert result == 0
        captured = capsys.readouterr()
        assert "hello%20world" in captured.out

    def test_html(self, capsys):
        result = main(["encode", "html", "<div>"])
        assert result == 0
        captured = capsys.readouterr()
        assert "&lt;div&gt;" in captured.out


class TestDecodeCommand:
    def test_base64(self, capsys):
        result = main(["decode", "b64", "SGVsbG8="])
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello" in captured.out

    def test_hex(self, capsys):
        result = main(["decode", "hex", "48656c6c6f"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello" in captured.out

    def test_url(self, capsys):
        result = main(["decode", "url", "hello%20world"])
        assert result == 0
        captured = capsys.readouterr()
        assert "hello world" in captured.out


class TestHashCommand:
    def test_sha256(self, capsys):
        result = main(["hash", "sha256", "hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out.strip()) == 64

    def test_md5(self, capsys):
        result = main(["hash", "md5", "hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out.strip()) == 32

    def test_all(self, capsys):
        result = main(["hash", "all", "hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert "md5" in captured.out.lower()
        assert "sha256" in captured.out.lower()


class TestHMACCommand:
    def test_hmac(self, capsys):
        result = main(["hmac", "sha256", "hello", "--key", "secret"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out.strip()) == 64

    def test_hmac_verify(self, capsys):
        from baseforge.hashing import compute_hmac

        hmac_val = compute_hmac("hello", "secret", "sha256")
        result = main(["hmac", "sha256", "hello", "--key", "secret", "--verify", hmac_val])
        assert result == 0
        captured = capsys.readouterr()
        assert "Valid" in captured.out


class TestCipherCommand:
    def test_rot13(self, capsys):
        result = main(["cipher", "rot13", "Hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Uryyb" in captured.out

    def test_caesar(self, capsys):
        result = main(["cipher", "caesar", "Hello", "--shift", "3"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Khoor" in captured.out

    def test_caesar_decrypt(self, capsys):
        result = main(["cipher", "caesar", "Khoor", "--shift", "3", "--decrypt"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello" in captured.out

    def test_atbash(self, capsys):
        result = main(["cipher", "atbash", "Hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Svool" in captured.out

    def test_analyze(self, capsys):
        result = main(["cipher", "analyze", "Hello World"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Cipher Information" in captured.out


class TestUUIDCommand:
    def test_generate(self, capsys):
        result = main(["uuid", "generate"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out.strip()) == 36

    def test_generate_count(self, capsys):
        result = main(["uuid", "generate", "--count", "5"])
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 5

    def test_validate(self, capsys):
        result = main(["uuid", "validate", "550e8400-e29b-41d4-a716-446655440000"])
        assert result == 0
        captured = capsys.readouterr()
        assert "valid" in captured.out.lower()


class TestTimestampCommand:
    def test_now(self, capsys):
        result = main(["timestamp", "now"])
        assert result == 0
        captured = capsys.readouterr()
        assert "T" in captured.out  # ISO format

    def test_info(self, capsys):
        result = main(["timestamp", "info", "1609459200"])
        assert result == 0
        captured = capsys.readouterr()
        assert "Timestamp Information" in captured.out


class TestDetectCommand:
    def test_detect(self, capsys):
        result = main(["detect", "SGVsbG8="])
        assert result == 0
        captured = capsys.readouterr()
        assert "base64" in captured.out.lower()


class TestBaseCommand:
    def test_hex_to_decimal(self, capsys):
        result = main(["base", "ff", "--from-base", "16", "--to-base", "10"])
        assert result == 0
        captured = capsys.readouterr()
        assert "255" in captured.out

    def test_decimal_to_hex(self, capsys):
        result = main(["base", "255", "--from-base", "10", "--to-base", "16"])
        assert result == 0
        captured = capsys.readouterr()
        assert "FF" in captured.out


class TestHexdumpCommand:
    def test_hexdump(self, capsys):
        result = main(["hexdump", "Hello"])
        assert result == 0
        captured = capsys.readouterr()
        assert "48 65 6c 6c 6f" in captured.out


class TestJSONOutput:
    def test_json_flag(self, capsys):
        result = main(["--json", "encode", "b64", "Hello"])
        assert result == 0
        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "SGVsbG8=" in data
