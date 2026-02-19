from easysun.utils.validation import (
    validate_wifi_ssid,
    validate_wifi_password,
    validate_datetime_string,
    validate_timestamp,
)


class TestValidateWifiSsid:
    def test_valid_ssid(self):
        assert validate_wifi_ssid("MyNetwork") == "MyNetwork"

    def test_valid_ssid_with_spaces(self):
        assert validate_wifi_ssid("My Network") == "My Network"

    def test_valid_ssid_with_special(self):
        assert validate_wifi_ssid("Net-Work_2.4") == "Net-Work_2.4"

    def test_empty(self):
        assert validate_wifi_ssid("") is None

    def test_none(self):
        assert validate_wifi_ssid(None) is None

    def test_too_long(self):
        assert validate_wifi_ssid("a" * 33) is None

    def test_injection_attempt(self):
        assert validate_wifi_ssid('test"; rm -rf /') is None

    def test_special_chars(self):
        assert validate_wifi_ssid("test@#$") is None


class TestValidateWifiPassword:
    def test_valid_password(self):
        assert validate_wifi_password("mypassword123") == "mypassword123"

    def test_min_length(self):
        assert validate_wifi_password("12345678") == "12345678"

    def test_too_short(self):
        assert validate_wifi_password("1234567") is None

    def test_too_long(self):
        assert validate_wifi_password("a" * 64) is None

    def test_empty(self):
        assert validate_wifi_password("") is None

    def test_none(self):
        assert validate_wifi_password(None) is None


class TestValidateDatetimeString:
    def test_valid(self):
        dt = validate_datetime_string("2024-01-15 14:30:00")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.hour == 14

    def test_invalid_format(self):
        assert validate_datetime_string("15/01/2024 14:30") is None

    def test_empty(self):
        assert validate_datetime_string("") is None

    def test_none(self):
        assert validate_datetime_string(None) is None

    def test_injection(self):
        assert validate_datetime_string('2024-01-15"; rm -rf /') is None


class TestValidateTimestamp:
    def test_valid(self):
        assert validate_timestamp("1700000000") == 1700000000

    def test_zero(self):
        assert validate_timestamp("0") == 0

    def test_negative(self):
        assert validate_timestamp("-1") is None

    def test_too_large(self):
        assert validate_timestamp("9999999999999") is None

    def test_not_a_number(self):
        assert validate_timestamp("abc") is None

    def test_none(self):
        assert validate_timestamp(None) is None
