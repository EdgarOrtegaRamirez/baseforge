"""JWT (JSON Web Token) operations."""

import base64
import hashlib
import hmac
import json
import time


class JWTError(Exception):
    """JWT-related error."""


def _base64url_decode(data: str) -> bytes:
    """Decode base64url-encoded data."""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded)


def _base64url_encode(data: bytes) -> str:
    """Encode data to base64url."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _get_algorithm_key(algorithm: str) -> bytes:
    """Get the HMAC hash function for an algorithm."""
    alg_map = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512,
    }
    if algorithm not in alg_map:
        raise JWTError(f"Unsupported algorithm: {algorithm}")
    return alg_map[algorithm]


def decode_jwt(token: str, verify: bool = False, secret: str | None = None) -> dict:
    """
    Decode a JWT token.

    Args:
        token: The JWT token string
        verify: Whether to verify the signature
        secret: The secret key for verification (required if verify=True)

    Returns:
        Dictionary with header, payload, and signature
    """
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise JWTError(f"Invalid JWT: expected 3 parts, got {len(parts)}")

    try:
        header_bytes = _base64url_decode(parts[0])
        header = json.loads(header_bytes)
    except Exception as e:
        raise JWTError(f"Invalid header: {e}") from e

    try:
        payload_bytes = _base64url_decode(parts[1])
        payload = json.loads(payload_bytes)
    except Exception as e:
        raise JWTError(f"Invalid payload: {e}") from e

    try:
        signature = _base64url_decode(parts[2])
    except Exception as e:
        raise JWTError(f"Invalid signature: {e}") from e

    # Verify signature if requested
    if verify:
        if secret is None:
            raise JWTError("Secret key required for verification")

        algorithm = header.get("alg", "")
        if algorithm.startswith("HS"):
            hash_fn = _get_algorithm_key(algorithm)
            signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
            expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hash_fn).digest()

            if not hmac.compare_digest(signature, expected_sig):
                raise JWTError("Signature verification failed")
        else:
            raise JWTError(f"Verification not supported for algorithm: {algorithm}")

    # Convert registered claims to readable format
    claims_info = {}
    claim_names = {
        "iss": "issuer",
        "sub": "subject",
        "aud": "audience",
        "exp": "expiration",
        "nbf": "not_before",
        "iat": "issued_at",
        "jti": "jwt_id",
    }
    for claim, name in claim_names.items():
        if claim in payload:
            value = payload[claim]
            if claim in ("exp", "nbf", "iat") and isinstance(value, (int, float)):
                claims_info[name] = {
                    "value": value,
                    "human": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(value)),
                    "relative": _relative_time(value),
                }
            else:
                claims_info[name] = value

    return {
        "header": header,
        "payload": payload,
        "signature": _base64url_encode(signature),
        "claims": claims_info,
        "valid": not verify or True,  # If we got here without exception, it's valid
    }


def _relative_time(timestamp: float) -> str:
    """Get human-readable relative time."""
    now = time.time()
    diff = timestamp - now
    if diff > 0:
        hours = int(diff // 3600)
        minutes = int((diff % 3600) // 60)
        if hours > 24:
            days = hours // 24
            return f"in {days} days, {hours % 24}h {minutes}m"
        return f"in {hours}h {minutes}m"
    else:
        abs_diff = abs(diff)
        hours = int(abs_diff // 3600)
        minutes = int((abs_diff % 3600) // 60)
        if hours > 24:
            days = hours // 24
            return f"{days} days, {hours % 24}h {minutes}m ago"
        return f"{hours}h {minutes}m ago"


def encode_jwt(
    payload: dict,
    secret: str,
    algorithm: str = "HS256",
    header: dict | None = None,
) -> str:
    """
    Encode a JWT token.

    Args:
        payload: The claims to include
        secret: The signing secret
        algorithm: The signing algorithm (HS256, HS384, HS512)
        header: Optional custom header

    Returns:
        The encoded JWT string
    """
    if header is None:
        header = {"alg": algorithm, "typ": "JWT"}
    else:
        header = dict(header)
        header["alg"] = algorithm
        if "typ" not in header:
            header["typ"] = "JWT"

    # Encode header
    header_b64 = _base64url_encode(json.dumps(header).encode("utf-8"))

    # Encode payload
    payload_b64 = _base64url_encode(json.dumps(payload).encode("utf-8"))

    # Create signature
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    hash_fn = _get_algorithm_key(algorithm)
    signature = hmac.new(secret.encode("utf-8"), signing_input, hash_fn).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def extract_claims(token: str) -> dict:
    """Extract claims from a JWT without verification."""
    result = decode_jwt(token, verify=False)
    return result["payload"]


def validate_jwt(token: str, secret: str) -> bool:
    """
    Validate a JWT token's signature and expiration.

    Returns:
        True if valid, False otherwise
    """
    try:
        result = decode_jwt(token, verify=True, secret=secret)

        # Check expiration
        payload = result["payload"]
        if "exp" in payload and time.time() > payload["exp"]:
            return False
        # Check not-before
        return not ("nbf" in payload and time.time() < payload["nbf"])
    except JWTError:
        return False


def jwt_info(token: str) -> str:
    """Get formatted information about a JWT token."""
    result = decode_jwt(token, verify=False)
    lines = ["JWT Token Information", "=" * 40]

    lines.append("\nHeader:")
    for key, value in result["header"].items():
        lines.append(f"  {key}: {value}")

    lines.append("\nPayload:")
    for key, value in result["payload"].items():
        if key in ("exp", "nbf", "iat") and isinstance(value, (int, float)):
            human = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(value))
            rel = _relative_time(value)
            lines.append(f"  {key}: {value} ({human}, {rel})")
        elif isinstance(value, (dict, list)):
            lines.append(f"  {key}: {json.dumps(value, indent=4)}")
        else:
            lines.append(f"  {key}: {value}")

    lines.append(f"\nSignature: {result['signature']}")
    lines.append(f"Algorithm: {result['header'].get('alg', 'unknown')}")
    lines.append(f"Token length: {len(token)} characters")

    return "\n".join(lines)
