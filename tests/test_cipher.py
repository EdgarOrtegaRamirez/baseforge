"""Tests for cipher module."""

from baseforge.cipher import (
    atbash,
    caesar_cipher,
    cipher_info,
    frequency_analysis,
    rot13,
    suggest_caesar_shift,
    vigenere_cipher,
)


class TestROT13:
    def test_basic(self):
        assert rot13("Hello World") == "Uryyb Jbeyq"

    def test_double_rot13(self):
        assert rot13(rot13("test")) == "test"

    def test_empty(self):
        assert rot13("") == ""

    def test_non_alpha(self):
        assert rot13("123!@#") == "123!@#"

    def test_mixed(self):
        assert rot13("Hello 123 World!") == "Uryyb 123 Jbeyq!"


class TestCaesarCipher:
    def test_encrypt(self):
        assert caesar_cipher("Hello", 3) == "Khoor"

    def test_decrypt(self):
        assert caesar_cipher("Khoor", 3, decrypt=True) == "Hello"

    def test_roundtrip(self):
        data = "The Quick Brown Fox"
        encrypted = caesar_cipher(data, 13)
        decrypted = caesar_cipher(encrypted, 13, decrypt=True)
        assert decrypted == data

    def test_shift_0(self):
        assert caesar_cipher("test", 0) == "test"

    def test_shift_26(self):
        assert caesar_cipher("test", 26) == "test"

    def test_negative_shift(self):
        assert caesar_cipher("Hello", -3) == "Ebiil"


class TestAtbash:
    def test_basic(self):
        assert atbash("Hello") == "Svool"

    def test_double_atbash(self):
        assert atbash(atbash("test")) == "test"

    def test_empty(self):
        assert atbash("") == ""

    def test_non_alpha(self):
        assert atbash("123!@#") == "123!@#"

    def test_mixed(self):
        assert atbash("Hello 123!") == "Svool 123!"


class TestVigenereCipher:
    def test_encrypt(self):
        result = vigenere_cipher("Hello", "KEY")
        assert isinstance(result, str)
        assert len(result) == 5

    def test_decrypt(self):
        encrypted = vigenere_cipher("Hello", "KEY")
        decrypted = vigenere_cipher(encrypted, "KEY", decrypt=True)
        assert decrypted == "Hello"

    def test_roundtrip(self):
        data = "Attack at dawn!"
        key = "LEMON"
        encrypted = vigenere_cipher(data, key)
        decrypted = vigenere_cipher(encrypted, key, decrypt=True)
        assert decrypted == data

    def test_non_alpha_preserved(self):
        result = vigenere_cipher("Hello, World!", "KEY")
        assert "," in result
        assert " " in result
        assert "!" in result


class TestFrequencyAnalysis:
    def test_basic(self):
        result = frequency_analysis("hello world")
        assert result["total_letters"] == 10
        assert "h" in result["frequencies"]
        assert "e" in result["frequencies"]

    def test_empty(self):
        result = frequency_analysis("")
        assert result["total_letters"] == 0

    def test_percentages(self):
        result = frequency_analysis("aaa")
        assert result["percentages"]["a"] == 100.0

    def test_chi_squared(self):
        result = frequency_analysis("the quick brown fox jumps over the lazy dog")
        assert result["chi_squared"] >= 0

    def test_english_reference(self):
        result = frequency_analysis("test")
        assert "english_reference" in result
        assert "a" in result["english_reference"]


class TestSuggestCaesarShift:
    def test_suggest(self):
        # Use longer text for better frequency analysis
        encrypted = caesar_cipher(
            "the quick brown fox jumps over the lazy dog and the other one too", 5
        )
        suggestions = suggest_caesar_shift(encrypted)
        # The correct shift should be in top 3
        top_shifts = [s[0] for s in suggestions[:3]]
        assert 5 in top_shifts

    def test_returns_all_shifts(self):
        suggestions = suggest_caesar_shift("test")
        assert len(suggestions) == 26


class TestCipherInfo:
    def test_info_format(self):
        info = cipher_info("Hello World")
        assert "Cipher Information" in info
        assert "ROT13:" in info
        assert "Atbash:" in info
        assert "Letter Frequency Analysis" in info
