"""
CareerAI — Career Analysis Routes

GET  /api/career/list      : catalog of all available careers
POST /api/career/analyze   : run recommendations from the user's profile
                             skills and persist the analysis
GET  /api/career/analysis  : fetch the most recent saved analysis
POST /api/career/gap       : detailed skill-gap analysis for one target
                             career (also saved to the profile)
"""

from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import profiles, career_analysis, roadmaps
from utils.career_engine import recommend_careers, analyze_skill_gap, list_careers
from utils.roadmap_engine import generate_roadmap, strip_quiz_answers

career_bp = Blueprint("career", __name__)

TOP_RECOMMENDATIONS = 6


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _get_user_skills(user_id):
    """Return (skills, error_response). Skills come from the profile."""
    profile_doc = profiles.find_one({"user_id": user_id})
    if not profile_doc:
        return None, (jsonify({"error": "Profile not found."}), 404)

    skills = profile_doc.get("current_skills", [])
    if not skills:
        return None, (
            jsonify(
                {
                    "error": "No skills found on your profile. "
                    "Upload your resume or add skills manually first."
                }
            ),
            422,
        )
    return skills, None


def _serialize_analysis(analysis_doc):
    payload = {
        "recommendations": analysis_doc["recommendations"],
        "skills_used": analysis_doc["skills_used"],
        "created_at": analysis_doc["created_at"].isoformat(),
    }

    if "target_career" in analysis_doc:
        payload["target_career"] = analysis_doc["target_career"]
    if "gap" in analysis_doc:
        payload["gap"] = analysis_doc["gap"]
    if "roadmap" in analysis_doc:
        payload["roadmap"] = analysis_doc["roadmap"]

    return payload


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@career_bp.route("/list", methods=["GET"])
@jwt_required()
def careers_catalog():
    return jsonify({"careers": list_careers()}), 200


@career_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    target_career = (data.get("career") or data.get("target_career") or "").strip()
    if not target_career:
        profile_doc = profiles.find_one({"user_id": user_id}) or {}
        target_career = (profile_doc.get("target_career") or "").strip()

    if not target_career:
        return (
            jsonify(
                {
                    "error": (
                        "Choose the role you're aiming for before analyzing your resume."
                    )
                }
            ),
            422,
        )

    skills, error = _get_user_skills(user_id)
    if error:
        return error

    recommendations = recommend_careers(skills, top_n=TOP_RECOMMENDATIONS)
    gap = analyze_skill_gap(skills, target_career)
    if gap is None:
        return jsonify({"error": f"Unknown career: '{target_career}'."}), 404

    roadmap = generate_roadmap(skills, gap["title"])
    if roadmap is None:
        return jsonify({"error": f"Unknown career: '{target_career}'."}), 404

    now = datetime.now(timezone.utc)

    roadmap["user_id"] = user_id
    roadmap["created_at"] = now
    roadmap["updated_at"] = now

    roadmaps.replace_one({"user_id": user_id}, roadmap, upsert=True)
    profiles.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "target_career": gap["title"],
                "updated_at": now,
            }
        },
    )

    analysis_doc = {
        "user_id": user_id,
        "skills_used": skills,
        "recommendations": recommendations,
        "target_career": gap["title"],
        "gap": gap,
        "roadmap": strip_quiz_answers(roadmap),
        "created_at": now,
    }
    career_analysis.insert_one(analysis_doc)

    return (
        jsonify(
            {
                "message": "Career analysis complete.",
                "analysis": _serialize_analysis(analysis_doc),
            }
        ),
        200,
    )


@career_bp.route("/analysis", methods=["GET"])
@jwt_required()
def latest_analysis():
    user_id = get_jwt_identity()

    # Compound index (user_id, created_at DESC) makes this query instant.
    analysis_doc = career_analysis.find_one(
        {"user_id": user_id}, sort=[("created_at", -1)]
    )

    if not analysis_doc:
        return (
            jsonify({"error": "No analysis found. Run an analysis first."}),
            404,
        )

    return jsonify({"analysis": _serialize_analysis(analysis_doc)}), 200


@career_bp.route("/gap", methods=["POST"])
@jwt_required()
def skill_gap():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    career_title = (data.get("career") or "").strip()
    if not career_title:
        return jsonify({"error": "A target career is required."}), 400

    skills, error = _get_user_skills(user_id)
    if error:
        return error

    gap = analyze_skill_gap(skills, career_title)
    if gap is None:
        return jsonify({"error": f"Unknown career: '{career_title}'."}), 404

    # Remember the user's chosen target career on their profile.
    profiles.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "target_career": gap["title"],
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return jsonify({"gap": gap}), 200
