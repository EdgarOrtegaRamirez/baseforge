"""Hash computation and HMAC operations."""

import hashlib
import hmac

# Supported hash algorithms
HASH_ALGORITHMS = {
    "md5": "md5",
    "sha1": "sha1",
    "sha224": "sha224",
    "sha256": "sha256",
    "sha384": "sha384",
    "sha512": "sha512",
    "sha3-224": "sha3_224",
    "sha3-256": "sha3_256",
    "sha3-384": "sha3_384",
    "sha3-512": "sha3_512",
    "blake2b": "blake2b",
    "blake2s": "blake2s",
}


def _get_hash_fn(name: str):
    """Get a hash function by name."""
    return getattr(hashlib, name)


def compute_hash(
    data: str,
    algorithm: str = "sha256",
    encoding: str = "hex",
) -> str:
    """
    Compute hash of data.

    Args:
        data: Input data to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512, etc.)
        encoding: Output encoding (hex, base64, base64url)

    Returns:
        Hash string
    """
    algorithm = algorithm.lower()
    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. "
            f"Supported: {', '.join(sorted(HASH_ALGORITHMS.keys()))}"
        )

    hash_fn = _get_hash_fn(HASH_ALGORITHMS[algorithm])()
    hash_fn.update(data.encode("utf-8"))
    digest = hash_fn.digest()

    if encoding == "base64":
        import base64

        return base64.b64encode(digest).decode("ascii")
    elif encoding == "base64url":
        import base64

        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    else:
        return digest.hex()


def compute_hmac(
    data: str,
    key: str,
    algorithm: str = "sha256",
    encoding: str = "hex",
) -> str:
    """
    Compute HMAC of data.

    Args:
        data: Input data to sign
        key: Secret key
        algorithm: Hash algorithm
        encoding: Output encoding

    Returns:
        HMAC string
    """
    algorithm = algorithm.lower()
    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    result = hmac.new(
        key.encode("utf-8"),
        data.encode("utf-8"),
        HASH_ALGORITHMS[algorithm],
    ).digest()

    if encoding == "base64":
        import base64

        return base64.b64encode(result).decode("ascii")
    elif encoding == "base64url":
        import base64

        return base64.urlsafe_b64encode(result).rstrip(b"=").decode("ascii")
    else:
        return result.hex()


def verify_hmac(
    data: str,
    key: str,
    expected_hmac: str,
    algorithm: str = "sha256",
) -> bool:
    """
    Verify HMAC is correct.

    Uses constant-time comparison to prevent timing attacks.
    """
    computed = compute_hmac(data, key, algorithm)
    return hmac.compare_digest(computed, expected_hmac)


def hash_info(data: str, algorithm: str = "sha256") -> str:
    """Get hash information for data across multiple algorithms."""
    lines = ["Hash Information", "=" * 40]
    lines.append(f"Input: {data[:100]}{'...' if len(data) > 100 else ''}")
    lines.append(f"Input length: {len(data)} bytes")
    lines.append("")

    # Compute hashes for all common algorithms
    for name in ["md5", "sha1", "sha256", "sha512", "sha3-256", "blake2b"]:
        try:
            h = compute_hash(data, name)
            lines.append(f"{name.upper():>8}: {h}")
        except Exception:
            pass

    return "\n".join(lines)


def hash_file(file_path: str, algorithm: str = "sha256", chunk_size: int = 8192) -> str:
    """
    Compute hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm
        chunk_size: Read chunk size

    Returns:
        Hash string
    """
    algorithm = algorithm.lower()
    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    hash_fn = _get_hash_fn(HASH_ALGORITHMS[algorithm])()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hash_fn.update(chunk)

    return hash_fn.hexdigest()
