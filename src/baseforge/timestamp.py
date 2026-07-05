"""Timestamp conversion and manipulation operations."""

import time
from datetime import datetime, timezone

# Common timestamp formats
TIMESTAMP_FORMATS = {
    "iso8601": "%Y-%m-%dT%H:%M:%S%z",
    "iso8601_short": "%Y-%m-%dT%H:%M:%S",
    "rfc2822": "%a, %d %b %Y %H:%M:%S %z",
    "date": "%Y-%m-%d",
    "time": "%H:%M:%S",
    "datetime": "%Y-%m-%d %H:%M:%S",
    "us_datetime": "%m/%d/%Y %H:%M:%S",
    "european_datetime": "%d/%m/%Y %H:%M:%S",
    "compact": "%Y%m%d%H%M%S",
    "filename": "%Y-%m-%d_%H-%M-%S",
    "log": "%d/%b/%Y:%H:%M:%S %z",
}


def parse_timestamp(value: str | int | float) -> datetime:
    """
    Parse a timestamp from various formats.

    Supports:
    - Unix timestamps (seconds, milliseconds, microseconds, nanoseconds)
    - ISO 8601 strings
    - Common date/time formats

    Returns:
        datetime object in UTC
    """
    if isinstance(value, (int, float)):
        return _from_unix(value)
    elif isinstance(value, str):
        return _from_string(value)
    else:
        raise ValueError(f"Cannot parse timestamp from {type(value)}")


def _from_unix(timestamp: int | float) -> datetime:
    """Convert Unix timestamp to datetime, auto-detecting precision."""
    # Auto-detect precision
    if timestamp > 1e18:
        # Nanoseconds
        timestamp = timestamp / 1e9
    elif timestamp > 1e15:
        # Microseconds
        timestamp = timestamp / 1e6
    elif timestamp > 1e12:
        # Milliseconds
        timestamp = timestamp / 1e3

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def _from_string(value: str) -> datetime:
    """Parse timestamp from string."""
    value = value.strip()

    # Try Unix timestamp (numeric string)
    try:
        ts = float(value)
        return _from_unix(ts)
    except ValueError:
        pass

    # Try ISO 8601 (most common)
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    # Try other common formats
    for _name, fmt in TIMESTAMP_FORMATS.items():
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    raise ValueError(f"Cannot parse timestamp: {value}")


def to_unix(dt: datetime, precision: str = "seconds") -> int | float:
    """
    Convert datetime to Unix timestamp.

    Args:
        dt: datetime object
        precision: 'seconds', 'milliseconds', 'microseconds', or 'nanoseconds'

    Returns:
        Unix timestamp as int or float
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    ts = dt.timestamp()

    if precision == "nanoseconds":
        return int(ts * 1e9)
    elif precision == "microseconds":
        return int(ts * 1e6)
    elif precision == "milliseconds":
        return int(ts * 1e3)
    else:
        return int(ts)


def format_timestamp(dt: datetime, fmt: str = "iso8601", tz: timezone | None = None) -> str:
    """
    Format a datetime to string.

    Args:
        dt: datetime object
        fmt: Format name or strftime format string
        tz: Target timezone (defaults to UTC)

    Returns:
        Formatted string
    """
    if tz is not None:
        dt = dt.astimezone(tz)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Check if it's a named format
    if fmt in TIMESTAMP_FORMATS:
        # Handle ISO8601 specially to get proper +00:00 format
        if fmt == "iso8601":
            return dt.strftime("%Y-%m-%dT%H:%M:%S") + _format_offset(dt)
        return dt.strftime(TIMESTAMP_FORMATS[fmt])
    # Otherwise treat as strftime format
    return dt.strftime(fmt)


def relative_time(dt: datetime, now: datetime | None = None) -> str:
    """Get human-readable relative time."""
    if now is None:
        now = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    diff = dt - now
    total_seconds = int(diff.total_seconds())
    is_future = total_seconds > 0
    abs_seconds = abs(total_seconds)

    if abs_seconds < 60:
        unit = "second"
        value = abs_seconds
    elif abs_seconds < 3600:
        unit = "minute"
        value = abs_seconds // 60
    elif abs_seconds < 86400:
        unit = "hour"
        value = abs_seconds // 3600
    elif abs_seconds < 2592000:  # 30 days
        unit = "day"
        value = abs_seconds // 86400
    elif abs_seconds < 31536000:  # 365 days
        unit = "month"
        value = abs_seconds // 2592000
    else:
        unit = "year"
        value = abs_seconds // 31536000

    if value != 1:
        unit += "s"

    if is_future:
        return f"in {value} {unit}"
    else:
        return f"{value} {unit} ago"


def _format_offset(dt: datetime) -> str:
    """Format timezone offset as +HH:MM."""
    if dt.tzinfo is None:
        return "+00:00"
    offset = dt.tzinfo.utcoffset(dt)
    if offset is None:
        return "+00:00"
    total_seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes, _ = divmod(remainder, 60)
    sign = "+" if total_seconds >= 0 else "-"
    return f"{sign}{hours:02d}:{minutes:02d}"


def timestamp_info(value: str | int | float) -> str:
    """Get formatted information about a timestamp."""
    dt = parse_timestamp(value)

    lines = ["Timestamp Information", "=" * 40]

    if isinstance(value, (int, float)):
        lines.append(f"Input (Unix): {value}")
    else:
        lines.append(f"Input: {value}")

    lines.append(f"\nParsed: {dt.isoformat()}")
    lines.append(f"UTC: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append(f"Local: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    lines.append("\nUnix Timestamps:")
    lines.append(f"  Seconds: {to_unix(dt, 'seconds')}")
    lines.append(f"  Milliseconds: {to_unix(dt, 'milliseconds')}")
    lines.append(f"  Microseconds: {to_unix(dt, 'microseconds')}")
    lines.append(f"  Nanoseconds: {to_unix(dt, 'nanoseconds')}")

    lines.append("\nCommon Formats:")
    for name, fmt in list(TIMESTAMP_FORMATS.items())[:8]:
        lines.append(f"  {name}: {format_timestamp(dt, fmt)}")

    lines.append(f"\nRelative: {relative_time(dt)}")

    # Day of week info
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    lines.append(f"Day of week: {days[dt.weekday()]}")
    lines.append(f"Day of year: {dt.timetuple().tm_yday}")
    lines.append(f"Week number: {dt.isocalendar()[1]}")

    return "\n".join(lines)


def now_info() -> str:
    """Get information about the current timestamp."""
    return timestamp_info(time.time())


def convert_timestamp(
    value: str | int | float,
    to_format: str = "iso8601",
    tz: timezone | None = None,
) -> str:
    """Convert a timestamp from one format to another."""
    dt = parse_timestamp(value)
    if to_format == "unix_seconds":
        return str(to_unix(dt, "seconds"))
    elif to_format == "unix_milliseconds":
        return str(to_unix(dt, "milliseconds"))
    elif to_format == "unix_microseconds":
        return str(to_unix(dt, "microseconds"))
    return format_timestamp(dt, to_format, tz)
