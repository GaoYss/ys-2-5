from flask import Blueprint, jsonify, request

from app.services.statistics import calculate_hour_stats


stats_bp = Blueprint("stats", __name__)


@stats_bp.get("/hours")
def hour_stats():
    class_id = request.args.get("class_id")
    teacher = request.args.get("teacher")
    room = request.args.get("room")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    results = calculate_hour_stats(
        class_id=class_id,
        teacher=teacher,
        room=room,
        date_from=date_from,
        date_to=date_to,
    )

    return jsonify({
        "items": results,
        "filters": {
            "class_id": class_id or None,
            "teacher": teacher or None,
            "room": room or None,
            "date_from": date_from or None,
            "date_to": date_to or None,
        },
    })
