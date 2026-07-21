"""
CareerAI — Learning Roadmap Routes

POST /api/roadmap/generate              : build (or rebuild) the user's roadmap
GET  /api/roadmap                       : fetch the current roadmap (quiz answers stripped)
PUT  /api/roadmap/module/<order>/start  : mark a module as in progress
POST /api/roadmap/module/<order>/quiz   : submit quiz answers — grading, scoring,
                                          completion, and progress logging
"""

from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import profiles, roadmaps, quiz_scores, progress
from utils.roadmap_engine import generate_roadmap, strip_quiz_answers, grade_quiz
from utils.resume_parser import SKILL_TAXONOMY

roadmap_bp = Blueprint("roadmap", __name__)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _find_module(roadmap_doc, order):
    """Return (module, index) for a module order number, or (None, -1)."""
    for index, module in enumerate(roadmap_doc.get("modules", [])):
        if module["order"] == order:
            return module, index
    return None, -1


def _previous_module_completed(roadmap_doc, order):
    """Only allow module N when module N-1 has been completed."""
    if order <= 1:
        return True

    previous_module, _ = _find_module(roadmap_doc, order - 1)
    if previous_module is None:
        return False

    return previous_module.get("status") == "completed"


def _log_progress(user_id, event_type, detail):
    """Append an activity event used by the analytics dashboard."""
    progress.insert_one(
        {
            "user_id": user_id,
            "type": event_type,  # module_started | module_completed | quiz_attempt
            "detail": detail,
            "date": datetime.now(timezone.utc),
        }
    )


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@roadmap_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    profile_doc = profiles.find_one({"user_id": user_id})
    if not profile_doc:
        return jsonify({"error": "Profile not found."}), 404

    # Explicit career in the request wins; otherwise use the saved target.
    career_title = (data.get("career") or profile_doc.get("target_career") or "").strip()
    if not career_title:
        return (
            jsonify(
                {
                    "error": "No target career selected. "
                    "Run a career analysis and choose a target first."
                }
            ),
            422,
        )

    skills = profile_doc.get("current_skills", [])
    roadmap = generate_roadmap(skills, career_title)
    if roadmap is None:
        return jsonify({"error": f"Unknown career: '{career_title}'."}), 404

    now = datetime.now(timezone.utc)
    roadmap["user_id"] = user_id
    roadmap["created_at"] = now
    roadmap["updated_at"] = now

    # One active roadmap per user (unique index) — regenerate replaces it.
    roadmaps.replace_one({"user_id": user_id}, roadmap, upsert=True)

    # Keep the profile's target career in sync.
    profiles.update_one(
        {"user_id": user_id},
        {"$set": {"target_career": roadmap["career"], "updated_at": now}},
    )

    return (
        jsonify(
            {
                "message": f"Roadmap generated for {roadmap['career']}.",
                "roadmap": strip_quiz_answers(roadmap),
            }
        ),
        201,
    )


@roadmap_bp.route("", methods=["GET"])
@jwt_required()
def get_roadmap():
    user_id = get_jwt_identity()

    roadmap_doc = roadmaps.find_one({"user_id": user_id})
    if not roadmap_doc:
        return (
            jsonify({"error": "No roadmap found. Generate one first."}),
            404,
        )

    return jsonify({"roadmap": strip_quiz_answers(roadmap_doc)}), 200


@roadmap_bp.route("/module/<int:order>/start", methods=["PUT"])
@jwt_required()
def start_module(order):
    user_id = get_jwt_identity()

    roadmap_doc = roadmaps.find_one({"user_id": user_id})
    if not roadmap_doc:
        return jsonify({"error": "No roadmap found."}), 404

    module, index = _find_module(roadmap_doc, order)
    if module is None:
        return jsonify({"error": f"Module {order} not found."}), 404

    if not _previous_module_completed(roadmap_doc, order):
        return (
            jsonify(
                {
                    "error": "Complete and pass the previous module quiz before starting this one."
                }
            ),
            409,
        )

    if module["status"] == "completed":
        return jsonify({"error": "This module is already completed."}), 409

    roadmaps.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"modules.{index}.status": "in_progress",
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    _log_progress(user_id, "module_started", {"module": module["skill"], "order": order})

    return jsonify({"message": f"Started learning {module['skill']}."}), 200


@roadmap_bp.route("/module/<int:order>/progress", methods=["PUT"])
@jwt_required()
def update_module_progress(order):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    roadmap_doc = roadmaps.find_one({"user_id": user_id})
    if not roadmap_doc:
        return jsonify({"error": "No roadmap found."}), 404

    module, index = _find_module(roadmap_doc, order)
    if module is None:
        return jsonify({"error": f"Module {order} not found."}), 404

    if not _previous_module_completed(roadmap_doc, order):
        return (
            jsonify(
                {
                    "error": "Pass the previous module quiz before progressing to this course."
                }
            ),
            409,
        )

    try:
        requested_percent = float(data.get("progress_percent", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "progress_percent must be a number."}), 400

    requested_percent = max(0, min(100, requested_percent))
    current_percent = float(module.get("progress_percent") or 0)
    capped_percent = min(requested_percent, 90)
    next_percent = max(current_percent, capped_percent)
    if module.get("status") == "completed":
        next_status = "completed"
    elif next_percent > 0:
        next_status = "in_progress"
    else:
        next_status = module.get("status", "not_started")
    now = datetime.now(timezone.utc)

    roadmaps.update_one(
        {"user_id": user_id},
        {
            "$set": {
                f"modules.{index}.progress_percent": round(next_percent, 1),
                f"modules.{index}.status": next_status,
                "updated_at": now,
            }
        },
    )

    _log_progress(
        user_id,
        "course_progress",
        {
            "module": module["skill"],
            "order": order,
            "progress_percent": round(next_percent, 1),
            "resource_type": data.get("resource_type", "course"),
            "resource_title": data.get("resource_title", ""),
        },
    )

    return (
        jsonify(
            {
                "message": f"Progress updated for {module['skill']}.",
                "module": {
                    "order": order,
                    "skill": module["skill"],
                    "status": next_status,
                    "progress_percent": round(next_percent, 1),
                },
            }
        ),
        200,
    )


@roadmap_bp.route("/module/<int:order>/quiz", methods=["POST"])
@jwt_required()
def submit_quiz(order):
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    answers = data.get("answers")

    roadmap_doc = roadmaps.find_one({"user_id": user_id})
    if not roadmap_doc:
        return jsonify({"error": "No roadmap found."}), 404

    module, index = _find_module(roadmap_doc, order)
    if module is None:
        return jsonify({"error": f"Module {order} not found."}), 404

    if not _previous_module_completed(roadmap_doc, order):
        return (
            jsonify(
                {
                    "error": "Pass the previous module quiz before attempting this one."
                }
            ),
            409,
        )

    quiz = module.get("quiz", [])
    now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Modules without a quiz (fallback resources) complete directly.
    # ------------------------------------------------------------------
    if not quiz:
        roadmaps.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"modules.{index}.status": "completed",
                    f"modules.{index}.progress_percent": 100,
                    "updated_at": now,
                }
            },
        )
        _log_progress(
            user_id, "module_completed", {"module": module["skill"], "order": order}
        )
        return (
            jsonify({"message": f"{module['skill']} marked as completed.", "passed": True}),
            200,
        )

    # ------------------------------------------------------------------
    # Grade the submission.
    # ------------------------------------------------------------------
    result = grade_quiz(quiz, answers)
    if result is None:
        return (
            jsonify(
                {"error": f"Please answer all {len(quiz)} questions before submitting."}
            ),
            400,
        )

    # Persist the attempt for analytics.
    quiz_scores.insert_one(
        {
            "user_id": user_id,
            "career": roadmap_doc["career"],
            "module_order": order,
            "skill": module["skill"],
            "score": result["score"],
            "total": result["total"],
            "percentage": result["percentage"],
            "passed": result["passed"],
            "created_at": now,
        }
    )
    _log_progress(
        user_id,
        "quiz_attempt",
        {"module": module["skill"], "order": order, "percentage": result["percentage"]},
    )

    updates = {
        f"modules.{index}.quiz_score": result["percentage"],
        "updated_at": now,
    }

    if result["passed"]:
        updates[f"modules.{index}.status"] = "completed"
        updates[f"modules.{index}.progress_percent"] = 100
        # A passed quiz proves the skill — add it to the user's profile.
        profiles.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"current_skills": module["skill"]},
                "$set": {"updated_at": now},
            },
        )
        _log_progress(
            user_id, "module_completed", {"module": module["skill"], "order": order}
        )
        message = f"Congratulations! You passed and mastered {module['skill']}."
    else:
        message = (
            f"You scored {result['percentage']}%. "
            f"You need 60% to pass — review the resources and try again."
        )

    roadmaps.update_one({"user_id": user_id}, {"$set": updates})

    return jsonify({"message": message, "result": result}), 200
