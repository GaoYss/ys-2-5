from flask import Blueprint, jsonify, request

from app.services.scheduler import (
    build_filter_suggestions,
    enrich_session,
    filter_schedule,
    generate_schedule,
)


schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.get("")
def list_schedule():
    class_id = request.args.get("class_id")
    teacher = request.args.get("teacher")
    room = request.args.get("room")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    results = filter_schedule(
        class_id=class_id,
        teacher=teacher,
        room=room,
        date_from=date_from,
        date_to=date_to,
    )

    suggestions = []
    if not results:
        suggestions = build_filter_suggestions(
            class_id=class_id,
            teacher=teacher,
            room=room,
            date_from=date_from,
            date_to=date_to,
        )

    return jsonify({
        "items": results,
        "suggestions": suggestions,
        "filters": {
            "class_id": class_id or None,
            "teacher": teacher or None,
            "room": room or None,
            "date_from": date_from or None,
            "date_to": date_to or None,
        },
    })


@schedule_bp.get("/filter-options")
def filter_options():
    from app.data.store import store

    teachers = set()
    rooms = set()
    for item in store.schedule:
        teachers.add(item["teacher"])
        rooms.add(item["room"])
    for item in store.classes:
        teachers.add(item["teacher"])
        rooms.add(item["room"])

    dates = sorted({item["date"] for item in store.schedule})

    return jsonify({
        "teachers": sorted(teachers),
        "rooms": sorted(rooms),
        "date_min": dates[0] if dates else None,
        "date_max": dates[-1] if dates else None,
    })


@schedule_bp.post("/generate")
def generate():
    payload = request.get_json() or {}
    generated = generate_schedule(
        class_id=payload.get("class_id"),
        days=int(payload.get("days", 8)),
    )
    return jsonify([enrich_session(item) for item in generated]), 201
