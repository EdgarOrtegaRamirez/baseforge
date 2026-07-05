"""Tests for UUID operations."""

import uuid

import pytest

from baseforge.uuid_ops import (
    batch_generate_uuids,
    generate_uuid,
    uuid_info,
    validate_uuid,
)


class TestUUIDGenerate:
    def test_generate_v4(self):
        result = generate_uuid(4)
        assert len(result) == 36
        assert result.count("-") == 4
        # Validate it's a proper UUID
        parsed = uuid.UUID(result)
        assert parsed.version == 4

    def test_generate_v1(self):
        result = generate_uuid(1)
        parsed = uuid.UUID(result)
        assert parsed.version == 1

    def test_generate_v3(self):
        result = generate_uuid(3, name="test.example.com")
        parsed = uuid.UUID(result)
        assert parsed.version == 3

    def test_generate_v5(self):
        result = generate_uuid(5, name="test.example.com")
        parsed = uuid.UUID(result)
        assert parsed.version == 5

    def test_generate_v5_namespace(self):
        ns = uuid.NAMESPACE_URL
        result = generate_uuid(5, name="test", namespace=str(ns))
        parsed = uuid.UUID(result)
        assert parsed.version == 5

    def test_generate_invalid_version(self):
        with pytest.raises(ValueError):
            generate_uuid(99)

    def test_deterministic_v3(self):
        result1 = generate_uuid(3, name="test", namespace=str(uuid.NAMESPACE_DNS))
        result2 = generate_uuid(3, name="test", namespace=str(uuid.NAMESPACE_DNS))
        assert result1 == result2

    def test_deterministic_v5(self):
        result1 = generate_uuid(5, name="test", namespace=str(uuid.NAMESPACE_DNS))
        result2 = generate_uuid(5, name="test", namespace=str(uuid.NAMESPACE_DNS))
        assert result1 == result2


class TestUUIDValidate:
    def test_valid_uuid(self):
        result = validate_uuid("550e8400-e29b-41d4-a716-446655440000")
        assert result["valid"] is True
        assert result["version"] == 4

    def test_invalid_format(self):
        result = validate_uuid("not-a-uuid")
        assert result["valid"] is False

    def test_empty_string(self):
        result = validate_uuid("")
        assert result["valid"] is False

    def test_v1_uuid(self):
        u = uuid.uuid1()
        result = validate_uuid(str(u))
        assert result["valid"] is True
        assert result["version"] == 1

    def test_v5_uuid(self):
        u = uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")
        result = validate_uuid(str(u))
        assert result["valid"] is True
        assert result["version"] == 5

    def test_nil_uuid(self):
        result = validate_uuid("00000000-0000-0000-0000-000000000000")
        assert result["valid"] is True
        assert result["is_nil"] is True

    def test_with_braces(self):
        result = validate_uuid("{550e8400-e29b-41d4-a716-446655440000}")
        assert result["valid"] is True


class TestUUIDInfo:
    def test_info_format(self):
        info = uuid_info("550e8400-e29b-41d4-a716-446655440000")
        assert "UUID Information" in info
        assert "Valid: Yes" in info

    def test_info_invalid(self):
        info = uuid_info("not-a-uuid")
        assert "Invalid UUID" in info

    def test_info_v1(self):
        u = uuid.uuid1()
        info = uuid_info(str(u))
        assert "Version: 1" in info
        assert "Time-based" in info


class TestBatchGenerate:
    def test_batch_v4(self):
        results = batch_generate_uuids(10, version=4)
        assert len(results) == 10
        # All should be unique
        assert len(set(results)) == 10

    def test_batch_v5(self):
        results = batch_generate_uuids(5, version=5)
        assert len(results) == 5
        # v5 is deterministic, so should all be unique (different names)
        assert len(set(results)) == 5
