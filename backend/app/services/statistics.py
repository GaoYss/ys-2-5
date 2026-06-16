from app.data.store import store
from app.services.scheduler import enrich_session, filter_schedule


ATTENDANCE_WEIGHT = {
    "present": 1,
    "late": 0.8,
    "leave": 0.5,
    "absent": 0,
}


def build_stats_suggestions(class_id=None, teacher=None, room=None, date_from=None, date_to=None):
    all_sessions = [enrich_session(item) for item in store.schedule]
    suggestions = []

    if not all_sessions:
        suggestions.append({
            "type": "info",
            "message": "系统内暂无排课记录，请先在「课程表」模块点击「自动生成课程表」创建排课后再查看统计。"
        })
        return suggestions

    if class_id:
        class_sessions = [item for item in all_sessions if item["class_id"] == int(class_id)]
        if not class_sessions:
            class_names = ", ".join(item["name"] for item in store.classes if any(
                s["class_id"] == item["id"] for s in all_sessions
            ))
            if class_names:
                suggestions.append({
                    "type": "class",
                    "message": f"当前班级暂无课次，可尝试切换到有课班级：{class_names}。"
                })
            else:
                suggestions.append({
                    "type": "class",
                    "message": "所选班级暂无排课记录，请先生成该班级的课程表。"
                })
        else:
            remaining = class_sessions
            if teacher:
                t_match = [item for item in remaining if item["teacher"] == teacher]
                if not t_match:
                    other_teachers = sorted(set(item["teacher"] for item in remaining))
                    suggestions.append({
                        "type": "teacher",
                        "message": f"该班级下没有「{teacher}」的授课统计，可尝试：{', '.join(other_teachers)}。"
                    })
                else:
                    remaining = t_match
            if room:
                r_match = [item for item in remaining if item["room"] == room]
                if not r_match:
                    other_rooms = sorted(set(item["room"] for item in remaining))
                    suggestions.append({
                        "type": "room",
                        "message": f"当前条件下「{room}」教室无统计数据，可尝试：{', '.join(other_rooms)}。"
                    })
                else:
                    remaining = r_match
            if date_from or date_to:
                d_match = remaining
                if date_from:
                    d_match = [item for item in d_match if item["date"] >= date_from]
                if date_to:
                    d_match = [item for item in d_match if item["date"] <= date_to]
                if not d_match:
                    dates = sorted(set(item["date"] for item in remaining))
                    if dates:
                        suggestions.append({
                            "type": "date",
                            "message": f"该日期范围内无统计数据，对应条件下有课日期：{dates[0]} 至 {dates[-1]}。"
                        })

    if not class_id and teacher:
        t_match = [item for item in all_sessions if item["teacher"] == teacher]
        if not t_match:
            other_teachers = sorted(set(item["teacher"] for item in all_sessions))
            suggestions.append({
                "type": "teacher",
                "message": f"没有「{teacher}」的授课统计，可尝试：{', '.join(other_teachers)}。"
            })

    if not class_id and room:
        r_match = [item for item in all_sessions if item["room"] == room]
        if not r_match:
            other_rooms = sorted(set(item["room"] for item in all_sessions))
            suggestions.append({
                "type": "room",
                "message": f"没有「{room}」教室的使用统计，可尝试：{', '.join(other_rooms)}。"
            })

    if (date_from or date_to) and not class_id and not teacher and not room:
        d_match = all_sessions
        if date_from:
            d_match = [item for item in d_match if item["date"] >= date_from]
        if date_to:
            d_match = [item for item in d_match if item["date"] <= date_to]
        if not d_match:
            dates = sorted(set(item["date"] for item in all_sessions))
            if dates:
                suggestions.append({
                    "type": "date",
                    "message": f"所选日期范围无统计数据，系统内有课日期：{dates[0]} 至 {dates[-1]}。"
                })

    if not suggestions:
        suggestions.append({
            "type": "info",
            "message": "当前筛选条件下暂无统计数据，请放宽筛选条件或先生成更多排课。"
        })

    return suggestions


def calculate_hour_stats(class_id=None, teacher=None, room=None, date_from=None, date_to=None):
    sessions = filter_schedule(
        class_id=class_id,
        teacher=teacher,
        room=room,
        date_from=date_from,
        date_to=date_to,
    )
    stats = []

    class_list = store.classes
    if class_id:
        class_list = [item for item in class_list if item["id"] == int(class_id)]

    for training_class in class_list:
        class_sessions = [
            item for item in sessions if item["class_id"] == training_class["id"]
        ]
        planned_hours = sum(item["duration"] for item in class_sessions)
        student_count = len(training_class["students"])
        attendance_records = [
            item
            for item in store.attendance
            if any(session["id"] == item["session_id"] for session in class_sessions)
        ]
        attended_hours = 0
        for record in attendance_records:
            session = next(
                item for item in class_sessions if item["id"] == record["session_id"]
            )
            attended_hours += session["duration"] * ATTENDANCE_WEIGHT.get(
                record["status"], 0
            )

        expected_total = planned_hours * student_count
        attendance_rate = round((attended_hours / expected_total) * 100, 1) if expected_total else 0

        stats.append(
            {
                "class_id": training_class["id"],
                "class_name": training_class["name"],
                "planned_hours": planned_hours,
                "student_count": student_count,
                "expected_total_hours": expected_total,
                "attended_hours": round(attended_hours, 1),
                "attendance_rate": attendance_rate,
            }
        )

    return stats
