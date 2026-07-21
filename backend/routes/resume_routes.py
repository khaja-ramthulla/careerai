"""
CareerAI — Resume Routes

POST /api/resume/upload     : validate + save the PDF, parse it, extract skills,
                               and merge results into the user's profile.
POST /api/resume/submit-form : accept manually-entered form data (skills,
                               education, experience, interests, target career)
                               and save to the profile just like a parsed resume.

The parsed skills are merged (union) with any skills the user added
manually, so uploading a resume never erases existing profile data.
"""

import os
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from database import profiles
from utils.resume_parser import parse_resume, SKILL_TAXONOMY
from utils.extensions import limiter

resume_bp = Blueprint("resume", __name__)

PDF_MAGIC_BYTES = b"%PDF"
TOP_RECOMMENDATIONS = 6


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def _is_real_pdf(file_storage):
    """Check the file's magic bytes, not just its extension."""
    header = file_storage.stream.read(4)
    file_storage.stream.seek(0)
    return header == PDF_MAGIC_BYTES


def _safe_remove(path):
    """Remove a file if it exists; ignore races with other cleanup paths."""
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def _remove_previous_resume(user_id, upload_folder):
    """Delete any resume previously uploaded by this user."""
    prefix = f"{user_id}_"
    try:
        for existing in os.listdir(upload_folder):
            if existing.startswith(prefix) and not existing.endswith(".part"):
                _safe_remove(os.path.join(upload_folder, existing))
    except OSError:
        # A cleanup failure must never block a new upload.
        pass


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@resume_bp.route("/upload", methods=["POST"])
@limiter.limit("5 per minute")
@jwt_required()
def upload_resume():
    user_id = get_jwt_identity()

    # --- Validate the request --------------------------------------
    if "resume" not in request.files:
        return jsonify({"error": "No file provided. Use the 'resume' field."}), 400

    file = request.files["resume"]

    if not file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    if not _is_real_pdf(file):
        return jsonify({"error": "This file is not a valid PDF."}), 400

    profile_doc = profiles.find_one({"user_id": user_id})
    if not profile_doc:
        return jsonify({"error": "Profile not found."}), 404

    # --- Save the new resume atomically -----------------------------
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    safe_name = secure_filename(file.filename) or "resume.pdf"
    stored_name = f"{user_id}_{safe_name}"
    temp_name = f"{stored_name}.part"
    temp_path = os.path.join(upload_folder, temp_name)
    final_path = os.path.join(upload_folder, stored_name)

    file.save(temp_path)

    # --- Parse the resume (before touching the old file) ------------
    try:
        parsed = parse_resume(temp_path)
    except ValueError as exc:
        _safe_remove(temp_path)
        return jsonify({"error": str(exc)}), 422

    # --- Now safe to remove the old resume and finalize the new one -
    _remove_previous_resume(user_id, upload_folder)
    os.replace(temp_path, final_path)

    # --- Merge results into the profile ------------------------------
    existing_skills = profile_doc.get("current_skills", [])
    merged_skills = sorted(
        {skill for skill in existing_skills} | set(parsed["skills"]),
        key=str.lower,
    )

    updates = {
        "current_skills": merged_skills,
        "resume_uploaded": True,
        "resume_filename": safe_name,
        "updated_at": datetime.now(timezone.utc),
    }

    # Fill education from the resume only if the user hasn't set it manually.
    if not profile_doc.get("education") and parsed["education"]:
        updates["education"] = parsed["education"][0]

    profiles.update_one({"user_id": user_id}, {"$set": updates})

    return (
        jsonify(
            {
                "message": "Resume analyzed successfully.",
                "parsed": {
                    "skills_found": parsed["skills"],
                    "skills_count": len(parsed["skills"]),
                    "education": parsed["education"],
                    "education_level": parsed["education_level"],
                    "experience_years": parsed["experience_years"],
                    "target_roles": parsed["target_roles"],
                    "email": parsed["email"],
                    "phone": parsed["phone"],
                    "word_count": parsed["word_count"],
                },
                "profile_skills": merged_skills,
            }
        ),
        200,
    )


# ----------------------------------------------------------------------
# POST /api/resume/submit-form
# Accept manually-entered profile data and save to the profile, producing
# the same payload shape as /upload so the frontend can continue into
# career analysis seamlessly.
# ----------------------------------------------------------------------
@resume_bp.route("/submit-form", methods=["POST"])
@limiter.limit("10 per minute")
@jwt_required()
def submit_profile_form():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    # --- Validate required fields ------------------------------------
    raw_skills = data.get("skills", [])
    if not isinstance(raw_skills, list) or len(raw_skills) == 0:
        return (
            jsonify({"error": "Please provide at least one skill."}),
            422,
        )

    target_career = (data.get("target_career") or "").strip()
    education = (data.get("education") or "").strip()
    interests = data.get("interests", [])

    # --- Normalize skills against the taxonomy ----------------------
    known = {name.lower(): name for name in SKILL_TAXONOMY}
    normalized = []
    unrecognized = []
    for skill in raw_skills:
        text = str(skill).strip()[:100]
        canonical = known.get(text.lower())
        if canonical:
            if canonical not in normalized:
                normalized.append(canonical)
        elif text:
            unrecognized.append(text)

    if not normalized:
        return (
            jsonify({
                "error": (
                    "None of the entered skills match our taxonomy. "
                    "Please use recognized skill names."
                ),
                "unrecognized": unrecognized,
                "valid_skills": sorted(SKILL_TAXONOMY.keys()),
            }),
            422,
        )

    # --- Normalize interests -----------------------------------------
    clean_interests = []
    if isinstance(interests, list):
        for item in interests[:30]:
            text = str(item).strip()[:100]
            if text and text not in clean_interests:
                clean_interests.append(text)

    # --- Merge into profile ------------------------------------------
    profile_doc = profiles.find_one({"user_id": user_id}) or {}
    existing_skills = profile_doc.get("current_skills", [])
    merged_skills = sorted(
        set(existing_skills) | set(normalized),
        key=str.lower,
    )

    now = datetime.now(timezone.utc)
    updates = {
        "current_skills": merged_skills,
        "resume_uploaded": False,
        "resume_filename": "",
        "updated_at": now,
    }

    if education:
        updates["education"] = education
    if target_career:
        updates["target_career"] = target_career
    if clean_interests:
        updates["interests"] = clean_interests

    profiles.update_one(
        {"user_id": user_id},
        {"$set": updates},
        upsert=True,
    )

    # Build a "parsed" shape that matches what the upload endpoint
    # returns so the frontend can feed it into renderTargetRoleAnalysisOnPage.
    parsed_shape = {
        "skills_found": normalized,
        "skills_count": len(normalized),
        "education": [education] if education else [],
        "education_level": [],
        "experience_years": None,
        "target_roles": [target_career] if target_career else [],
        "email": "",
        "phone": "",
        "word_count": 0,
    }

    return (
        jsonify({
            "message": "Profile saved successfully.",
            "parsed": parsed_shape,
            "profile_skills": merged_skills,
            "warnings": (
                {"unrecognized_skills": unrecognized} if unrecognized else None
            ),
        }),
        200,
    )
