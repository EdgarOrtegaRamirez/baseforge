"""Tests for JWT operations."""

import time

import pytest

from baseforge.jwt_ops import (
    JWTError,
    decode_jwt,
    encode_jwt,
    extract_claims,
    jwt_info,
    validate_jwt,
)


class TestJWTDecode:
    def test_decode_valid_token(self):
        token = encode_jwt({"sub": "1234567890", "name": "John"}, "secret")
        result = decode_jwt(token)
        assert result["payload"]["sub"] == "1234567890"
        assert result["payload"]["name"] == "John"
        assert result["header"]["alg"] == "HS256"
        assert result["header"]["typ"] == "JWT"

    def test_decode_with_claims(self):
        payload = {
            "sub": "1234567890",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "iss": "baseforge",
        }
        token = encode_jwt(payload, "secret")
        result = decode_jwt(token)
        assert "claims" in result
        assert result["claims"]["issuer"] == "baseforge"
        assert "expiration" in result["claims"]

    def test_decode_invalid_token(self):
        with pytest.raises(JWTError):
            decode_jwt("invalid.token")

    def test_decode_wrong_parts(self):
        with pytest.raises(JWTError):
            decode_jwt("only.two")


class TestJWTEncode:
    def test_encode_basic(self):
        token = encode_jwt({"data": "test"}, "secret")
        parts = token.split(".")
        assert len(parts) == 3

    def test_encode_algorithms(self):
        for alg in ["HS256", "HS384", "HS512"]:
            token = encode_jwt({"test": True}, "secret", algorithm=alg)
            result = decode_jwt(token)
            assert result["header"]["alg"] == alg

    def test_encode_custom_header(self):
        token = encode_jwt({"test": True}, "secret", header={"custom": "value"})
        result = decode_jwt(token)
        assert result["header"]["custom"] == "value"

    def test_roundtrip(self):
        payload = {"sub": "user123", "role": "admin", "iat": int(time.time())}
        token = encode_jwt(payload, "my-secret-key")
        decoded = decode_jwt(token)
        assert decoded["payload"]["sub"] == "user123"
        assert decoded["payload"]["role"] == "admin"


class TestJWTVerify:
    def test_valid_signature(self):
        token = encode_jwt({"valid": True}, "correct-secret")
        assert decode_jwt(token, verify=True, secret="correct-secret")["valid"] is True

    def test_invalid_signature(self):
        token = encode_jwt({"valid": True}, "correct-secret")
        with pytest.raises(JWTError, match="Signature verification failed"):
            decode_jwt(token, verify=True, secret="wrong-secret")

    def test_verify_without_secret(self):
        token = encode_jwt({"test": True}, "secret")
        with pytest.raises(JWTError, match="Secret key required"):
            decode_jwt(token, verify=True)

    def test_validate_jwt_function(self):
        token = encode_jwt({"test": True}, "secret")
        assert validate_jwt(token, "secret") is True
        assert validate_jwt(token, "wrong") is False


class TestJWTExtractClaims:
    def test_extract_basic(self):
        payload = {"sub": "user1", "name": "Test"}
        token = encode_jwt(payload, "secret")
        claims = extract_claims(token)
        assert claims["sub"] == "user1"
        assert claims["name"] == "Test"

    def test_extract_with_timestamps(self):
        now = int(time.time())
        payload = {"exp": now + 3600, "iat": now}
        token = encode_jwt(payload, "secret")
        claims = extract_claims(token)
        assert "exp" in claims
        assert "iat" in claims


class TestJWTInfo:
    def test_info_format(self):
        token = encode_jwt({"sub": "user1", "iss": "test"}, "secret")
        info = jwt_info(token)
        assert "JWT Token Information" in info
        assert "sub: user1" in info
        assert "iss: test" in info
        assert "HS256" in info
