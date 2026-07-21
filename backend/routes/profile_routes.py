"""
CareerAI — Profile Routes

GET /api/profile  : fetch the authenticated user's profile
PUT /api/profile  : update education, interests, skills, target career
"""

from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import profiles
from utils.resume_parser import SKILL_TAXONOMY

profile_bp = Blueprint("profile", __name__)

MAX_TEXT_LENGTH = 200
MAX_LIST_ITEMS = 50


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _serialize_profile(profile_doc):
    """Return a JSON-friendly view of a profile document."""
    return {
        "user_id": profile_doc["user_id"],
        "education": profile_doc.get("education", ""),
        "interests": profile_doc.get("interests", []),
        "current_skills": profile_doc.get("current_skills", []),
        "target_career": profile_doc.get("target_career", ""),
        "resume_uploaded": profile_doc.get("resume_uploaded", False),
        "resume_filename": profile_doc.get("resume_filename", ""),
        "updated_at": profile_doc["updated_at"].isoformat(),
    }


def _clean_text(value):
    """Coerce a value to a trimmed, length-capped string."""
    return str(value).strip()[:MAX_TEXT_LENGTH]


def _clean_string_list(value):
    """
    Coerce a value into a deduplicated list of clean, non-empty strings.
    Returns None if the value is not a list (validation failure).
    """
    if not isinstance(value, list):
        return None

    cleaned = []
    seen = set()
    for item in value[:MAX_LIST_ITEMS]:
        text = _clean_text(item)
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@profile_bp.route("", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()

    profile_doc = profiles.find_one({"user_id": user_id})
    if not profile_doc:
        return jsonify({"error": "Profile not found."}), 404

    return jsonify({"profile": _serialize_profile(profile_doc)}), 200


@profile_bp.route("", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    updates = {}
    skill_warnings = None

    # --- Simple text fields -------------------------------------------
    if "education" in data:
        updates["education"] = _clean_text(data["education"])

    if "target_career" in data:
        updates["target_career"] = _clean_text(data["target_career"])

    # --- List fields ---------------------------------------------------
    if "interests" in data:
        interests = _clean_string_list(data["interests"])
        if interests is None:
            return jsonify({"error": "Interests must be a list of strings."}), 400
        updates["interests"] = interests

    if "current_skills" in data:
        skills = _clean_string_list(data["current_skills"])
        if skills is None:
            return jsonify({"error": "Skills must be a list of strings."}), 400
        # Normalize to canonical taxonomy names (case-insensitive match).
        known = {name.lower(): name for name in SKILL_TAXONOMY}
        normalized = []
        unknown = []
        for skill in skills:
            canonical = known.get(skill.lower())
            if canonical:
                if canonical not in normalized:
                    normalized.append(canonical)
            else:
                unknown.append(skill)
        updates["current_skills"] = normalized
        if unknown:
            skill_warnings = {
                "unrecognized_skills": unknown,
                "valid_skills": sorted(SKILL_TAXONOMY.keys()),
            }

    if not updates:
        return jsonify({"error": "No valid fields provided to update."}), 400

    updates["updated_at"] = datetime.now(timezone.utc)

    result = profiles.find_one_and_update(
        {"user_id": user_id},
        {"$set": updates},
        return_document=True,
    )

    if not result:
        return jsonify({"error": "Profile not found."}), 404

    payload = {
        "message": "Profile updated successfully.",
        "profile": _serialize_profile(result),
    }
    if skill_warnings:
        payload["warnings"] = skill_warnings

    return jsonify(payload), 200
