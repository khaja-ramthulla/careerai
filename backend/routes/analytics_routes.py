"""
CareerAI — Analytics & Progress Routes

GET /api/analytics/summary      : full dashboard payload — profile stats,
                                  roadmap progress, quiz performance,
                                  7-day activity chart, recent activity feed
GET /api/analytics/quiz-history : chronological quiz attempts (for charts)
"""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import profiles, roadmaps, quiz_scores, progress, career_analysis

analytics_bp = Blueprint("analytics", __name__)

WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
RECENT_ACTIVITY_LIMIT = 10
QUIZ_HISTORY_LIMIT = 50


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _roadmap_stats(user_id):
    """Progress numbers derived from the user's roadmap document."""
    roadmap_doc = roadmaps.find_one({"user_id": user_id})
    if not roadmap_doc:
        return {
            "has_roadmap": False,
            "career": None,
            "total_modules": 0,
            "completed_modules": 0,
            "in_progress_modules": 0,
            "completion_percentage": 0.0,
            "total_weeks": 0,
        }

    modules = roadmap_doc.get("modules", [])
    completed = sum(1 for m in modules if m["status"] == "completed")
    in_progress = sum(1 for m in modules if m["status"] == "in_progress")
    total = len(modules)
    progress_sum = sum(
        100 if m["status"] == "completed" else float(m.get("progress_percent") or 0)
        for m in modules
    )

    return {
        "has_roadmap": True,
        "career": roadmap_doc["career"],
        "total_modules": total,
        "completed_modules": completed,
        "in_progress_modules": in_progress,
        "completion_percentage": round(progress_sum / total, 1) if total else 100.0,
        "total_weeks": roadmap_doc.get("total_weeks", 0),
    }


def _quiz_stats(user_id):
    """Aggregate quiz performance across all attempts."""
    attempts = list(quiz_scores.find({"user_id": user_id}))
    if not attempts:
        return {"attempts": 0, "passed": 0, "average_percentage": 0.0, "best_percentage": 0.0}

    percentages = [attempt["percentage"] for attempt in attempts]
    return {
        "attempts": len(attempts),
        "passed": sum(1 for attempt in attempts if attempt["passed"]),
        "average_percentage": round(sum(percentages) / len(percentages), 1),
        "best_percentage": max(percentages),
    }


def _weekly_activity(user_id):
    """
    Activity counts for the last 7 days (including today),
    shaped for a Chart-style bar chart: labels + counts.
    """
    now = datetime.now(timezone.utc)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today - timedelta(days=6)

    events = progress.find(
        {"user_id": user_id, "date": {"$gte": week_start}},
        {"date": 1},
    )

    counts = {}
    for event in events:
        event_date = event["date"]
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)
        key = event_date.date().isoformat()
        counts[key] = counts.get(key, 0) + 1

    labels, values = [], []
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        labels.append(WEEKDAY_LABELS[day.weekday()])
        values.append(counts.get(day.date().isoformat(), 0))

    return {"labels": labels, "values": values}


def _recent_activity(user_id):
    """Latest activity events for the dashboard feed."""
    events = progress.find(
        {"user_id": user_id}, sort=[("date", -1)], limit=RECENT_ACTIVITY_LIMIT
    )
    return [
        {
            "type": event["type"],
            "detail": event.get("detail", {}),
            "date": event["date"].isoformat(),
        }
        for event in events
    ]


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@analytics_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    user_id = get_jwt_identity()

    profile_doc = profiles.find_one({"user_id": user_id})
    if not profile_doc:
        return jsonify({"error": "Profile not found."}), 404

    latest_analysis = career_analysis.find_one(
        {"user_id": user_id}, sort=[("created_at", -1)]
    )
    top_match = None
    if latest_analysis and latest_analysis.get("recommendations"):
        best = latest_analysis["recommendations"][0]
        top_match = {"title": best["title"], "match_score": best["match_score"]}

    return (
        jsonify(
            {
                "profile": {
                    "skills_count": len(profile_doc.get("current_skills", [])),
                    "skills": profile_doc.get("current_skills", []),
                    "target_career": profile_doc.get("target_career", ""),
                    "resume_uploaded": profile_doc.get("resume_uploaded", False),
                },
                "top_match": top_match,
                "roadmap": _roadmap_stats(user_id),
                "quizzes": _quiz_stats(user_id),
                "weekly_activity": _weekly_activity(user_id),
                "recent_activity": _recent_activity(user_id),
            }
        ),
        200,
    )


@analytics_bp.route("/quiz-history", methods=["GET"])
@jwt_required()
def quiz_history():
    user_id = get_jwt_identity()

    attempts = quiz_scores.find(
        {"user_id": user_id}, sort=[("created_at", 1)], limit=QUIZ_HISTORY_LIMIT
    )

    history = [
        {
            "skill": attempt["skill"],
            "career": attempt["career"],
            "percentage": attempt["percentage"],
            "passed": attempt["passed"],
            "date": attempt["created_at"].isoformat(),
        }
        for attempt in attempts
    ]

    return jsonify({"history": history}), 200
