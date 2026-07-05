"""Tests for hashing module."""

import os
import tempfile

import pytest

from baseforge.hashing import (
    compute_hash,
    compute_hmac,
    hash_file,
    hash_info,
    verify_hmac,
)


class TestComputeHash:
    def test_sha256(self):
        result = compute_hash("hello", "sha256")
        assert len(result) == 64
        assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_md5(self):
        result = compute_hash("hello", "md5")
        assert len(result) == 32

    def test_sha512(self):
        result = compute_hash("hello", "sha512")
        assert len(result) == 128

    def test_blake2b(self):
        result = compute_hash("hello", "blake2b")
        assert len(result) == 128

    def test_sha3_256(self):
        result = compute_hash("hello", "sha3-256")
        assert len(result) == 64

    def test_base64_encoding(self):
        result = compute_hash("hello", "sha256", "base64")
        assert "+" in result or "/" in result or "=" in result

    def test_base64url_encoding(self):
        result = compute_hash("hello", "sha256", "base64url")
        assert "+" not in result and "/" not in result

    def test_empty_string(self):
        result = compute_hash("", "sha256")
        assert len(result) == 64

    def test_unicode(self):
        result = compute_hash("日本語", "sha256")
        assert len(result) == 64

    def test_invalid_algorithm(self):
        with pytest.raises(ValueError):
            compute_hash("hello", "invalid")


class TestComputeHMAC:
    def test_hmac_sha256(self):
        result = compute_hmac("hello", "key", "sha256")
        assert len(result) == 64

    def test_hmac_md5(self):
        result = compute_hmac("hello", "key", "md5")
        assert len(result) == 32

    def test_hmac_base64(self):
        result = compute_hmac("hello", "key", "sha256", "base64")
        assert isinstance(result, str)

    def test_deterministic(self):
        r1 = compute_hmac("data", "key")
        r2 = compute_hmac("data", "key")
        assert r1 == r2

    def test_different_keys(self):
        r1 = compute_hmac("data", "key1")
        r2 = compute_hmac("data", "key2")
        assert r1 != r2


class TestVerifyHMAC:
    def test_valid(self):
        data = "test data"
        key = "secret"
        expected = compute_hmac(data, key)
        assert verify_hmac(data, key, expected) is True

    def test_invalid(self):
        assert verify_hmac("data", "key", "wrong_hmac") is False

    def test_different_data(self):
        hmac_val = compute_hmac("data1", "key")
        assert verify_hmac("data2", "key", hmac_val) is False


class TestHashInfo:
    def test_info_format(self):
        info = hash_info("test")
        assert "Hash Information" in info
        assert "MD5:" in info
        assert "SHA256:" in info
        assert "SHA512:" in info

    def test_info_with_input(self):
        info = hash_info("hello world")
        assert "hello world" in info


class TestHashFile:
    def test_hash_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("test content")
            tmp_path = f.name

        try:
            result = hash_file(tmp_path, "sha256")
            assert len(result) == 64

            # Same content should produce same hash
            result2 = hash_file(tmp_path, "sha256")
            assert result == result2
        finally:
            os.unlink(tmp_path)

    def test_hash_file_different_algorithms(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("test content")
            tmp_path = f.name

        try:
            md5 = hash_file(tmp_path, "md5")
            sha256 = hash_file(tmp_path, "sha256")
            assert md5 != sha256
            assert len(md5) == 32
            assert len(sha256) == 64
        finally:
            os.unlink(tmp_path)
