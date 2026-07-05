"""Tests for timestamp operations."""

from datetime import datetime, timedelta, timezone

import pytest

from baseforge.timestamp import (
    convert_timestamp,
    format_timestamp,
    now_info,
    parse_timestamp,
    relative_time,
    timestamp_info,
    to_unix,
)


class TestParseTimestamp:
    def test_parse_unix_seconds(self):
        dt = parse_timestamp(1609459200)
        assert dt.year == 2021
        assert dt.month == 1
        assert dt.day == 1

    def test_parse_unix_milliseconds(self):
        dt = parse_timestamp(1609459200000)
        assert dt.year == 2021

    def test_parse_unix_microseconds(self):
        dt = parse_timestamp(1609459200000000)
        assert dt.year == 2021

    def test_parse_unix_string(self):
        dt = parse_timestamp("1609459200")
        assert dt.year == 2021

    def test_parse_iso8601(self):
        dt = parse_timestamp("2021-01-01T00:00:00Z")
        assert dt.year == 2021
        assert dt.month == 1
        assert dt.day == 1

    def test_parse_iso8601_no_z(self):
        dt = parse_timestamp("2021-01-01T00:00:00")
        assert dt.year == 2021

    def test_parse_date_only(self):
        dt = parse_timestamp("2021-06-15")
        assert dt.year == 2021
        assert dt.month == 6
        assert dt.day == 15

    def test_parse_datetime(self):
        dt = parse_timestamp("2021-06-15 14:30:00")
        assert dt.hour == 14
        assert dt.minute == 30

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            parse_timestamp("not-a-timestamp")

    def test_parse_with_offset(self):
        dt = parse_timestamp("2021-01-01T00:00:00+05:00")
        assert dt.tzinfo is not None


class TestToUnix:
    def test_to_seconds(self):
        dt = datetime(2021, 1, 1, tzinfo=timezone.utc)
        assert to_unix(dt, "seconds") == 1609459200

    def test_to_milliseconds(self):
        dt = datetime(2021, 1, 1, tzinfo=timezone.utc)
        assert to_unix(dt, "milliseconds") == 1609459200000

    def test_to_microseconds(self):
        dt = datetime(2021, 1, 1, tzinfo=timezone.utc)
        assert to_unix(dt, "microseconds") == 1609459200000000

    def test_to_nanoseconds(self):
        dt = datetime(2021, 1, 1, tzinfo=timezone.utc)
        assert to_unix(dt, "nanoseconds") == 1609459200000000000

    def test_naive_datetime(self):
        dt = datetime(2021, 1, 1)
        ts = to_unix(dt)
        assert isinstance(ts, int)


class TestFormatTimestamp:
    def test_iso8601(self):
        dt = datetime(2021, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_timestamp(dt, "iso8601")
        assert "2021-06-15T14:30:00+00:00" in result

    def test_date(self):
        dt = datetime(2021, 6, 15, tzinfo=timezone.utc)
        result = format_timestamp(dt, "date")
        assert result == "2021-06-15"

    def test_custom_format(self):
        dt = datetime(2021, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_timestamp(dt, "%Y/%m/%d %H:%M")
        assert result == "2021/06/15 14:30"

    def test_filename_format(self):
        dt = datetime(2021, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_timestamp(dt, "filename")
        assert result == "2021-06-15_14-30-00"


class TestRelativeTime:
    def test_future_seconds(self):
        dt = datetime.now(timezone.utc) + timedelta(seconds=30)
        result = relative_time(dt)
        assert "in" in result
        assert "second" in result

    def test_future_hours(self):
        dt = datetime.now(timezone.utc) + timedelta(hours=2)
        result = relative_time(dt)
        assert "in" in result
        assert "hour" in result

    def test_past_days(self):
        dt = datetime.now(timezone.utc) - timedelta(days=5)
        result = relative_time(dt)
        assert "ago" in result
        assert "day" in result

    def test_past_months(self):
        dt = datetime.now(timezone.utc) - timedelta(days=60)
        result = relative_time(dt)
        assert "ago" in result
        assert "month" in result


class TestTimestampInfo:
    def test_info_format(self):
        info = timestamp_info(1609459200)
        assert "Timestamp Information" in info
        assert "Unix Timestamps:" in info
        assert "Common Formats:" in info

    def test_info_with_string(self):
        info = timestamp_info("2021-01-01T00:00:00Z")
        assert "2021-01-01" in info

    def test_now_info(self):
        info = now_info()
        assert "Timestamp Information" in info


class TestConvertTimestamp:
    def test_convert(self):
        result = convert_timestamp(1609459200, "date")
        assert result == "2021-01-01"

    def test_convert_to_unix(self):
        result = convert_timestamp("2021-01-01", "unix_seconds")
        # Should return a numeric string
        assert result.isdigit() or result.lstrip("-").isdigit()
