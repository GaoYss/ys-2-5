from datetime import date, timedelta

from app.data.store import store


TIME_SLOTS = ["09:00-11:00", "14:00-16:00", "19:00-21:00"]


def filter_schedule(class_id=None, teacher=None, room=None, date_from=None, date_to=None):
    results = [enrich_session(item) for item in store.schedule]

    if class_id:
        results = [item for item in results if item["class_id"] == int(class_id)]
    if teacher:
        results = [item for item in results if item["teacher"] == teacher]
    if room:
        results = [item for item in results if item["room"] == room]
    if date_from:
        results = [item for item in results if item["date"] >= date_from]
    if date_to:
        results = [item for item in results if item["date"] <= date_to]

    return results


def build_filter_suggestions(class_id=None, teacher=None, room=None, date_from=None, date_to=None):
    all_sessions = [enrich_session(item) for item in store.schedule]
    suggestions = []

    if not all_sessions:
        suggestions.append({"type": "info", "message": "课程表为空，请先点击「自动生成课程表」创建排课记录。"})
        return suggestions

    if class_id:
        class_match = [item for item in all_sessions if item["class_id"] == int(class_id)]
        if not class_match:
            suggestions.append({"type": "class", "message": "当前筛选的班级暂无课程，可尝试切换其他班级。"})
        else:
            remaining = class_match
            if teacher:
                t_match = [item for item in remaining if item["teacher"] == teacher]
                if not t_match:
                    other_teachers = sorted(set(item["teacher"] for item in remaining))
                    suggestions.append({
                        "type": "teacher",
                        "message": f"该班级下没有「{teacher}」的课程，可尝试：{', '.join(other_teachers)}。"
                    })
                else:
                    remaining = t_match
            if room:
                r_match = [item for item in remaining if item["room"] == room]
                if not r_match:
                    other_rooms = sorted(set(item["room"] for item in remaining))
                    suggestions.append({
                        "type": "room",
                        "message": f"当前条件下没有「{room}」教室的课，可尝试：{', '.join(other_rooms)}。"
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
                            "message": f"日期范围内无课程，该条件下有课的日期：{dates[0]} 至 {dates[-1]}。"
                        })

    if not class_id and teacher:
        t_match = [item for item in all_sessions if item["teacher"] == teacher]
        if not t_match:
            other_teachers = sorted(set(item["teacher"] for item in all_sessions))
            suggestions.append({
                "type": "teacher",
                "message": f"没有「{teacher}」的课程，可尝试：{', '.join(other_teachers)}。"
            })

    if not class_id and room:
        r_match = [item for item in all_sessions if item["room"] == room]
        if not r_match:
            other_rooms = sorted(set(item["room"] for item in all_sessions))
            suggestions.append({
                "type": "room",
                "message": f"没有「{room}」教室的课程，可尝试：{', '.join(other_rooms)}。"
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
                    "message": f"日期范围内无课程，系统内有课的日期：{dates[0]} 至 {dates[-1]}。"
                })

    if not suggestions:
        suggestions.append({"type": "info", "message": "没有匹配的课程，请放宽筛选条件或先生成更多课次。"})

    return suggestions


def generate_schedule(class_id=None, days=10):
    classes = store.classes
    if class_id:
        classes = [item for item in classes if item["id"] == int(class_id)]

    if not classes:
        return []

    generated = []
    cursor = date.today() + timedelta(days=1)
    course_index = 0

    while len(generated) < days:
        if cursor.weekday() < 5:
            for training_class in classes:
                course = store.courses[course_index % len(store.courses)]
                session = {
                    "id": store.next_id("schedule"),
                    "class_id": training_class["id"],
                    "course_id": course["id"],
                    "date": cursor.isoformat(),
                    "time": TIME_SLOTS[course_index % len(TIME_SLOTS)],
                    "room": training_class["room"],
                    "teacher": training_class["teacher"],
                }
                store.schedule.append(session)
                generated.append(session)
                course_index += 1
                if len(generated) >= days:
                    break
        cursor += timedelta(days=1)

    return generated


def enrich_session(session):
    training_class = next(
        (item for item in store.classes if item["id"] == session["class_id"]), None
    )
    course = next((item for item in store.courses if item["id"] == session["course_id"]), None)
    return {
        **session,
        "class_name": training_class["name"] if training_class else "未知班级",
        "course_title": course["title"] if course else "未知课程",
        "duration": course["duration"] if course else 0,
    }
