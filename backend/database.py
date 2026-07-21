"""
CareerAI — MongoDB Atlas Connection Layer

Single shared PyMongo client for the whole application.
Collections are created automatically by MongoDB on first insert;
indexes below are idempotent and safe to (re)create on every boot.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING

from config import Config

# ----------------------------------------------------------------------
# Client & database handle
# serverSelectionTimeoutMS keeps startup errors fast and readable
# instead of hanging for 30s when Atlas is unreachable.
# ----------------------------------------------------------------------
_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=8000)
db = _client[Config.DB_NAME]

# ----------------------------------------------------------------------
# Collections
# ----------------------------------------------------------------------
users = db["users"]
profiles = db["profiles"]
career_analysis = db["career_analysis"]
roadmaps = db["roadmaps"]
resources = db["resources"]
quiz_scores = db["quiz_scores"]
progress = db["progress"]
contact_submissions = db["contact_submissions"]


def init_indexes():
    """
    Create all indexes required by the application.

    - users.email          : unique, enforces no duplicate registrations
    - profiles.user_id     : unique, one profile per user
    - career_analysis      : latest analysis per user fetched quickly
    - roadmaps.user_id     : unique, one active roadmap per user
    - progress             : per-user activity queried by date
    - quiz_scores          : per-user quiz history, newest first
    - contact_submissions   : contact form entries
    """
    users.create_index([("email", ASCENDING)], unique=True)
    profiles.create_index([("user_id", ASCENDING)], unique=True)
    career_analysis.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)]
    )
    roadmaps.create_index([("user_id", ASCENDING)], unique=True)
    progress.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
    quiz_scores.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    contact_submissions.create_index([("created_at", DESCENDING)])


def ping():
    """Return True if MongoDB Atlas is reachable (used for diagnostics)."""
    try:
        _client.admin.command("ping")
        return True
    except Exception:
        return False
