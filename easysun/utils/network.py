import re
import subprocess


def configure_wifi(ssid, password):
    """Write wpa_supplicant.conf with validated SSID and password.

    Returns True on success, False on failure.
    """
    content = (
        "country=fr\n"
        "update_config=1\n"
        "ctrl_interface=/var/run/wpa_supplicant\n\n"
        "network={\n"
        "    scan_ssid=1\n"
        f'    ssid="{ssid}"\n'
        f'    psk="{password}"\n'
        "}\n"
    )
    try:
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
            f.write(content)
        return True
    except OSError:
        return False


def set_system_datetime(dt_str):
    """Set system date safely using subprocess argument list.

    Returns True on success, False on failure.
    """
    try:
        result = subprocess.run(
            ["sudo", "date", "-s", dt_str],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def get_wlan_ip():
    """Get the wlan0 IP address. Returns IP string or None."""
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show", "wlan0"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", result.stdout)
        return match.group(1) if match else None
    except (subprocess.TimeoutExpired, OSError):
        return None
