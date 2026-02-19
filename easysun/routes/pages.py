from flask import Blueprint, render_template, redirect, request

pages_bp = Blueprint("pages", __name__)

# IP address of the RPi on the hotspot network
HOTSPOT_IP = "192.168.0.254"


@pages_bp.route("/")
def index():
    return redirect("/dashboard")


@pages_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", active_page="dashboard")


@pages_bp.route("/history")
def history():
    return render_template("history.html", active_page="history")


@pages_bp.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


# --- Captive portal detection ---
# Android, iOS, Windows and macOS probe specific URLs to detect captive portals.
# By redirecting these probes to our dashboard, the device shows a
# "Sign in to network" popup that opens our web interface.

@pages_bp.route("/generate_204")
@pages_bp.route("/gen_204")
def android_captive():
    """Android captive portal detection."""
    return redirect(f"http://{HOTSPOT_IP}/dashboard")


@pages_bp.route("/hotspot-detect.html")
def apple_captive():
    """iOS/macOS captive portal detection."""
    return redirect(f"http://{HOTSPOT_IP}/dashboard")


@pages_bp.route("/connecttest.txt")
@pages_bp.route("/ncsi.txt")
def windows_captive():
    """Windows captive portal detection."""
    return redirect(f"http://{HOTSPOT_IP}/dashboard")


@pages_bp.route("/canonical.html")
def firefox_captive():
    """Firefox captive portal detection."""
    return redirect(f"http://{HOTSPOT_IP}/dashboard")


@pages_bp.before_app_request
def captive_portal_redirect():
    """Redirect any request to an unknown host to the dashboard.

    When dnsmasq resolves all DNS to the RPi, browsers will send requests
    with Host headers like 'google.com'. We redirect those to our dashboard.
    """
    host = request.host.split(":")[0]
    # If the request is not for our IP or localhost, redirect
    if host not in (HOTSPOT_IP, "localhost", "127.0.0.1"):
        return redirect(f"http://{HOTSPOT_IP}/dashboard")