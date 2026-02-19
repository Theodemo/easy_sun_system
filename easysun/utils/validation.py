import re
from datetime import datetime


def validate_wifi_ssid(ssid):
    """Return cleaned SSID or None if invalid."""
    if not ssid or not isinstance(ssid, str):
        return None
    ssid = ssid.strip()
    if len(ssid) == 0 or len(ssid) > 32:
        return None
    if not re.match(r"^[a-zA-Z0-9 _\-\.]+$", ssid):
        return None
    return ssid


def validate_wifi_password(password):
    """Return cleaned password or None if invalid (WPA2: 8-63 printable ASCII)."""
    if not password or not isinstance(password, str):
        return None
    if len(password) < 8 or len(password) > 63:
        return None
    if not re.match(r"^[\x20-\x7E]+$", password):
        return None
    return password


def validate_datetime_string(dt_str):
    """Parse and validate a datetime string. Returns datetime or None."""
    if not dt_str or not isinstance(dt_str, str):
        return None
    try:
        return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def validate_timestamp(value):
    """Validate that a value is a reasonable Unix timestamp. Returns int or None."""
    try:
        ts = int(value)
        if ts < 0 or ts > 4102444800:  # year 2100
            return None
        return ts
    except (ValueError, TypeError):
        return None
