"""UUID generation and parsing operations."""

import re
import uuid

# UUID version constants
UUID_VERSIONS = {
    1: "Time-based (MAC address)",
    3: "Name-based (MD5)",
    4: "Random",
    5: "Name-based (SHA-1)",
}


def generate_uuid(version: int = 4, **kwargs) -> str:
    """
    Generate a UUID.

    Args:
        version: UUID version (1, 3, 4, or 5)
        **kwargs: Additional arguments based on version
            - For v3/v5: name (str), namespace (uuid.UUID or str)
            - For v1: node (optional), clock_seq (optional)

    Returns:
        UUID string in standard format
    """
    if version == 1:
        return str(uuid.uuid1(**kwargs))
    elif version == 3:
        name = kwargs.get("name", "")
        namespace = kwargs.get("namespace", uuid.NAMESPACE_DNS)
        if isinstance(namespace, str):
            namespace = uuid.UUID(namespace)
        return str(uuid.uuid3(namespace, name))
    elif version == 4:
        return str(uuid.uuid4())
    elif version == 5:
        name = kwargs.get("name", "")
        namespace = kwargs.get("namespace", uuid.NAMESPACE_DNS)
        if isinstance(namespace, str):
            namespace = uuid.UUID(namespace)
        return str(uuid.uuid5(namespace, name))
    else:
        raise ValueError(f"Unsupported UUID version: {version}")


def validate_uuid(uuid_str: str) -> dict:
    """
    Validate and analyze a UUID string.

    Returns:
        Dictionary with validation results and UUID info
    """
    result = {
        "input": uuid_str,
        "valid": False,
        "version": None,
        "variant": None,
        "fields": None,
        "hex": None,
        "int": None,
        "is_nil": False,
    }

    # Clean the input
    cleaned = uuid_str.strip().strip("{}").lower()

    # Check format
    if not re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", cleaned):
        return result

    try:
        u = uuid.UUID(cleaned)
        result["valid"] = True
        result["version"] = u.version
        result["variant"] = str(u.variant)
        result["hex"] = u.hex
        result["int"] = u.int
        result["is_nil"] = u == uuid.UUID(int=0)

        # Extract fields
        result["fields"] = {
            "time_low": f"{u.time_low:08x}",
            "time_mid": f"{u.time_mid:04x}",
            "time_hi_version": f"{u.time_hi_version:04x}",
            "clock_seq_hi_variant": f"{u.clock_seq_hi_variant:02x}",
            "clock_seq_low": f"{u.clock_seq_low:02x}",
            "node": f"{u.node:012x}",
        }

        # Version-specific info
        if u.version == 1:
            result["timestamp"] = str(u.time)
            result["node"] = f"{u.node:012x}"
        elif u.version in (3, 5):
            result["namespace"] = str(u.node)  # namespace UUID
            result["name_hash"] = f"{u.time:032x}"

    except ValueError:
        pass

    return result


def uuid_info(uuid_str: str) -> str:
    """Get formatted information about a UUID."""
    result = validate_uuid(uuid_str)

    if not result["valid"]:
        return f"Invalid UUID: {uuid_str}"

    lines = ["UUID Information", "=" * 40]
    lines.append(f"Input: {result['input']}")
    lines.append("Valid: Yes")
    lines.append(
        f"Version: {result['version']} ({UUID_VERSIONS.get(result['version'], 'unknown')})"
    )
    lines.append(f"Variant: {result['variant']}")
    lines.append(f"Is Nil: {result['is_nil']}")

    if result["fields"]:
        lines.append("\nFields:")
        for key, value in result["fields"].items():
            lines.append(f"  {key}: {value}")

    lines.append(f"\nHex (no dashes): {result['hex']}")
    lines.append(f"Integer: {result['int']}")

    if result["version"] == 1:
        lines.append(f"\nTimestamp: {result.get('timestamp', 'N/A')}")
        lines.append(f"Node (MAC): {result.get('node', 'N/A')}")

    return "\n".join(lines)


def batch_generate_uuids(count: int, version: int = 4, namespace: str | None = None) -> list:
    """
    Generate multiple UUIDs.

    Args:
        count: Number of UUIDs to generate
        version: UUID version
        namespace: Namespace for v3/v5 (defaults to NAMESPACE_DNS)

    Returns:
        List of UUID strings
    """
    ns = uuid.NAMESPACE_DNS
    if namespace:
        ns = uuid.UUID(namespace)

    results = []
    for i in range(count):
        if version in (3, 5):
            results.append(generate_uuid(version, name=f"item-{i}", namespace=ns))
        else:
            results.append(generate_uuid(version))
    return results
