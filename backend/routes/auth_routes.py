"""
CareerAI — Authentication Routes

POST /api/auth/register : create account (bcrypt-hashed password) + empty profile
POST /api/auth/login    : verify credentials, return JWT access token
GET  /api/auth/me       : return the authenticated user's details
"""

import re
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo.errors import DuplicateKeyError

from database import users, profiles
from utils.extensions import bcrypt, limiter

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
PASSWORD_MIN_LENGTH = 6
NAME_MIN_LENGTH = 2


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _serialize_user(user_doc):
    """Return a safe, JSON-friendly view of a user document (no password)."""
    created = user_doc.get("created_at")
    return {
        "id": str(user_doc["_id"]),
        "name": user_doc.get("name", ""),
        "email": user_doc.get("email", ""),
        "created_at": created.isoformat() if created else None,
    }


def _validate_registration(name, email, password):
    """Return an error message string, or None if the payload is valid."""
    if len(name) < NAME_MIN_LENGTH:
        return "Please enter your full name."
    if not EMAIL_REGEX.match(email):
        return "Please enter a valid email address."
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    return None


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    error = _validate_registration(name, email, password)
    if error:
        return jsonify({"error": error}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    now = datetime.now(timezone.utc)

    try:
        result = users.insert_one(
            {
                "name": name,
                "email": email,
                "password_hash": password_hash,
                "created_at": now,
            }
        )
    except DuplicateKeyError:
        # Unique index on users.email guarantees this even under race conditions.
        return jsonify({"error": "An account with this email already exists."}), 409

    user_id = str(result.inserted_id)

    # Every user gets an empty profile immediately (one-to-one, unique index).
    profiles.insert_one(
        {
            "user_id": user_id,
            "education": "",
            "interests": [],
            "current_skills": [],
            "target_career": "",
            "resume_uploaded": False,
            "resume_filename": "",
            "created_at": now,
            "updated_at": now,
        }
    )

    token = create_access_token(identity=user_id)
    user_doc = users.find_one({"_id": result.inserted_id})

    return (
        jsonify(
            {
                "message": "Account created successfully.",
                "access_token": token,
                "user": _serialize_user(user_doc),
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("15 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user_doc = users.find_one({"email": email})

    # Same error for unknown email and wrong password — never leak which one.
    # Support legacy "password" field from older registrations.
    if not user_doc:
        return jsonify({"error": "Invalid email or password."}), 401

    stored_hash = user_doc.get("password_hash") or user_doc.get("password")
    if not stored_hash or not bcrypt.check_password_hash(stored_hash, password):
        return jsonify({"error": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user_doc["_id"]))

    return (
        jsonify(
            {
                "message": "Login successful.",
                "access_token": token,
                "user": _serialize_user(user_doc),
            }
        ),
        200,
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()

    try:
        user_doc = users.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
        return jsonify({"error": "Invalid user identity."}), 401

    if not user_doc:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"user": _serialize_user(user_doc)}), 200
