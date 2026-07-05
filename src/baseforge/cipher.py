"""Classical cipher operations."""


def rot13(data: str) -> str:
    """Apply ROT13 cipher."""
    result = []
    for char in data:
        if "a" <= char <= "z":
            result.append(chr((ord(char) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= char <= "Z":
            result.append(chr((ord(char) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(char)
    return "".join(result)


def caesar_cipher(data: str, shift: int, decrypt: bool = False) -> str:
    """
    Apply Caesar cipher.

    Args:
        data: Input text
        shift: Number of positions to shift (1-25)
        decrypt: If True, reverse the shift

    Returns:
        Encrypted/decrypted text
    """
    if decrypt:
        shift = -shift

    result = []
    for char in data:
        if "a" <= char <= "z":
            result.append(chr((ord(char) - ord("a") + shift) % 26 + ord("a")))
        elif "A" <= char <= "Z":
            result.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
        else:
            result.append(char)
    return "".join(result)


def atbash(data: str) -> str:
    """Apply Atbash cipher (A↔Z, B↔Y, etc.)."""
    result = []
    for char in data:
        if "a" <= char <= "z":
            result.append(chr(ord("z") - (ord(char) - ord("a"))))
        elif "A" <= char <= "Z":
            result.append(chr(ord("Z") - (ord(char) - ord("A"))))
        else:
            result.append(char)
    return "".join(result)


def vigenere_cipher(data: str, key: str, decrypt: bool = False) -> str:
    """
    Apply Vigenere cipher.

    Args:
        data: Input text
        key: Encryption key (letters only)
        decrypt: If True, decrypt instead of encrypt

    Returns:
        Encrypted/decrypted text
    """
    key = key.lower()
    key_idx = 0
    result = []

    for char in data:
        if "a" <= char <= "z":
            shift = ord(key[key_idx % len(key)]) - ord("a")
            if decrypt:
                shift = -shift
            result.append(chr((ord(char) - ord("a") + shift) % 26 + ord("a")))
            key_idx += 1
        elif "A" <= char <= "Z":
            shift = ord(key[key_idx % len(key)]) - ord("a")
            if decrypt:
                shift = -shift
            result.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)


def frequency_analysis(data: str) -> dict:
    """
    Perform letter frequency analysis.

    Returns:
        Dictionary with letter frequencies and statistics
    """
    # Count letters
    freq = {}
    total = 0
    for char in data.lower():
        if "a" <= char <= "z":
            freq[char] = freq.get(char, 0) + 1
            total += 1

    # Calculate percentages
    percentages = {}
    for char, count in freq.items():
        percentages[char] = (count / total * 100) if total > 0 else 0

    # English letter frequencies for reference
    english_freq = {
        "a": 8.167,
        "b": 1.492,
        "c": 2.782,
        "d": 4.253,
        "e": 12.702,
        "f": 2.228,
        "g": 2.015,
        "h": 6.094,
        "i": 6.966,
        "j": 0.153,
        "k": 0.772,
        "l": 4.025,
        "m": 2.406,
        "n": 6.749,
        "o": 7.507,
        "p": 1.929,
        "q": 0.095,
        "r": 5.987,
        "s": 6.327,
        "t": 9.056,
        "u": 2.758,
        "v": 0.978,
        "w": 2.360,
        "x": 0.150,
        "y": 1.974,
        "z": 0.074,
    }

    return {
        "frequencies": dict(sorted(freq.items())),
        "percentages": dict(sorted(percentages.items())),
        "total_letters": total,
        "unique_letters": len(freq),
        "english_reference": english_freq,
        "chi_squared": _chi_squared(freq, total),
    }


def _chi_squared(observed: dict, total: int) -> float:
    """Calculate chi-squared statistic against English letter frequencies."""
    english_freq = {
        "a": 8.167,
        "b": 1.492,
        "c": 2.782,
        "d": 4.253,
        "e": 12.702,
        "f": 2.228,
        "g": 2.015,
        "h": 6.094,
        "i": 6.966,
        "j": 0.153,
        "k": 0.772,
        "l": 4.025,
        "m": 2.406,
        "n": 6.749,
        "o": 7.507,
        "p": 1.929,
        "q": 0.095,
        "r": 5.987,
        "s": 6.327,
        "t": 9.056,
        "u": 2.758,
        "v": 0.978,
        "w": 2.360,
        "x": 0.150,
        "y": 1.974,
        "z": 0.074,
    }

    chi2 = 0.0
    for letter in "abcdefghijklmnopqrstuvwxyz":
        observed_count = observed.get(letter, 0)
        expected_count = (english_freq[letter] / 100) * total
        if expected_count > 0:
            chi2 += (observed_count - expected_count) ** 2 / expected_count

    return chi2


def suggest_caesar_shift(data: str) -> list:
    """
    Try all Caesar cipher shifts and suggest the most likely one.

    Returns:
        List of (shift, chi_squared, decoded_text) tuples, sorted by chi-squared
    """
    results = []
    for shift in range(26):
        decoded = caesar_cipher(data, shift, decrypt=True)
        freq = frequency_analysis(decoded)
        results.append((shift, freq["chi_squared"], decoded))

    return sorted(results, key=lambda x: x[1])


def cipher_info(data: str, cipher_type: str = "all") -> str:
    """Get information about cipher operations on data."""
    lines = ["Cipher Information", "=" * 40]
    lines.append(f"Input: {data[:100]}{'...' if len(data) > 100 else ''}")
    lines.append(f"Input length: {len(data)} characters")

    if cipher_type in ("rot13", "all"):
        lines.append(f"\nROT13: {rot13(data)}")

    if cipher_type in ("atbash", "all"):
        lines.append(f"Atbash: {atbash(data)}")

    if cipher_type in ("caesar", "all"):
        # Try common shifts
        lines.append("\nCaesar shifts:")
        suggestions = suggest_caesar_shift(data)
        for shift, chi2, decoded in suggestions[:5]:
            lines.append(f"  Shift {shift:2d} (χ²={chi2:.1f}): {decoded[:80]}")

    # Frequency analysis
    freq = frequency_analysis(data)
    if freq["total_letters"] > 0:
        lines.append("\nLetter Frequency Analysis:")
        lines.append(f"  Total letters: {freq['total_letters']}")
        lines.append(f"  Unique letters: {freq['unique_letters']}")
        lines.append(f"  Chi-squared vs English: {freq['chi_squared']:.2f}")
        lines.append("  Most common letters:")
        sorted_freq = sorted(freq["percentages"].items(), key=lambda x: -x[1])
        for letter, pct in sorted_freq[:5]:
            lines.append(f"    {letter}: {pct:.1f}%")

    return "\n".join(lines)
