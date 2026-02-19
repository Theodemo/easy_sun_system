from flask import Blueprint, jsonify, request, current_app

from ..services.reader import get_reader
from ..database.repository import query_register_values
from ..utils.validation import validate_timestamp

api_bp = Blueprint("api", __name__)


@api_bp.route("/update")
def update():
    """Return current register values for real-time display."""
    reader = get_reader(current_app)
    data = reader.read_all_display()
    return jsonify(data)


@api_bp.route("/chart-data")
def chart_data():
    """Return historical data for charts."""
    start = validate_timestamp(request.args.get("start_datetime"))
    end = validate_timestamp(request.args.get("end_datetime"))
    if start is None or end is None:
        return jsonify({"error": "Invalid timestamps"}), 400

    db_path = current_app.config["DATABASE_PATH"]
    v_chargw, t_chargw, sum_chargw = query_register_values(
        db_path, "CHARGW", start, end
    )
    v_loadw, t_loadw, sum_loadw = query_register_values(db_path, "LOADW", start, end)

    return jsonify(
        {
            "chargw": {
                "values": v_chargw,
                "timestamps": t_chargw,
                "total_sum": sum_chargw,
            },
            "loadw": {
                "values": v_loadw,
                "timestamps": t_loadw,
                "total_sum": sum_loadw,
            },
        }
    )
