from flask import Blueprint, request, jsonify, current_app

from ..utils.validation import (
    validate_wifi_ssid,
    validate_wifi_password,
    validate_datetime_string,
)
from ..utils.network import configure_wifi, set_system_datetime, get_wlan_ip
from ..database.repository import clear_all_data

system_bp = Blueprint("system", __name__)


@system_bp.route("/configure-wifi", methods=["POST"])
def configure_wifi_route():
    """Configure Wi-Fi with validated SSID and password."""
    data = request.get_json() or {}
    ssid = validate_wifi_ssid(data.get("ssid", ""))
    password = validate_wifi_password(data.get("password", ""))
    if not ssid or not password:
        return jsonify({"error": "SSID ou mot de passe invalide."}), 400

    success = configure_wifi(ssid, password)
    if success:
        return jsonify({"message": "Configuration Wi-Fi appliquee avec succes."})
    return jsonify({"error": "Impossible d'ecrire la configuration."}), 500


@system_bp.route("/update-datetime", methods=["POST"])
def update_datetime():
    """Update system date and time with validation."""
    data = request.get_json() or {}
    dt = validate_datetime_string(data.get("datetime", ""))
    if not dt:
        return (
            jsonify(
                {"error": "Format invalide. Utilisez AAAA-MM-JJ HH:MM:SS."}
            ),
            400,
        )

    success = set_system_datetime(dt.strftime("%Y-%m-%d %H:%M:%S"))
    if success:
        return jsonify(
            {"message": "L'heure et la date ont ete mises a jour avec succes."}
        )
    return jsonify({"error": "Impossible de mettre a jour l'heure systeme."}), 500


@system_bp.route("/clear-data", methods=["POST"])
def clear_data():
    """Clear all data from the database. Requires confirmation."""
    data = request.get_json() or {}
    if not data.get("confirm"):
        return (
            jsonify({"error": 'Envoyez {"confirm": true} pour confirmer.'}),
            400,
        )

    clear_all_data(current_app.config["DATABASE_PATH"])
    return jsonify(
        {
            "message": "Toutes les donnees ont ete effacees et la base de donnees optimisee."
        }
    )


@system_bp.route("/check-connection")
def check_connection():
    """Check Wi-Fi connection status."""
    wlan_ip = get_wlan_ip()
    if wlan_ip:
        message = (
            f"La Centrale est connectee. "
            f"Accedez a la page depuis http://{wlan_ip}:5000."
        )
    else:
        message = "La Centrale n'est pas connectee au reseau Wi-Fi."
    return jsonify({"message": message})
