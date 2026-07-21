"""
CareerAI - Contact Routes

POST /api/contact/submit : validate a contact message, persist it, and send it
                           to the configured recipient email.
"""

from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib

from flask import Blueprint, jsonify, request, current_app

from database import contact_submissions
from utils.extensions import limiter

contact_bp = Blueprint("contact", __name__)


def _send_contact_email(name, email, message):
    host = current_app.config.get("SMTP_HOST", "")
    port = int(current_app.config.get("SMTP_PORT", 587))
    username = current_app.config.get("SMTP_USER", "")
    password = current_app.config.get("SMTP_PASSWORD", "")
    use_tls = bool(current_app.config.get("SMTP_USE_TLS", True))
    sender = current_app.config.get("SMTP_FROM_EMAIL", username or "no-reply@careerai.local")
    recipient = current_app.config.get("CONTACT_RECIPIENT_EMAIL")

    if not host:
        return False, "SMTP host is not configured."
    if not recipient:
        return False, "Contact recipient email is not configured."

    subject = f"CareerAI contact form: {name}"
    body = (
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Received: {datetime.now(timezone.utc).isoformat()}\n\n"
        f"Message:\n{message}\n"
    )

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = sender
    email_message["To"] = recipient
    email_message["Reply-To"] = email
    email_message.set_content(body)

    with smtplib.SMTP(host, port, timeout=15) as smtp:
        if use_tls:
            smtp.starttls()
        if username:
            smtp.login(username, password)
        smtp.send_message(email_message)

    return True, None


@contact_bp.route("/submit", methods=["POST"])
@limiter.limit("5 per minute")
def submit_contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    # Honeypot: bots fill this hidden field; real users leave it blank.
    if data.get("website"):
        return jsonify({"error": "Thanks!"}), 200

    if len(name) < 2 or len(name) > 100:
        return jsonify({"error": "Please enter your full name (2-100 characters)."}), 400
    if len(email) < 5 or len(email) > 254 or "@" not in email:
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(message) < 10 or len(message) > 5000:
        return jsonify({"error": "Message must be 10-5000 characters."}), 400

    submission = {
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime.now(timezone.utc),
        "status": "pending",
    }
    inserted = contact_submissions.insert_one(submission)

    try:
        sent, reason = _send_contact_email(name, email, message)
    except Exception as exc:
        contact_submissions.update_one(
            {"_id": inserted.inserted_id},
            {"$set": {"status": "failed", "failure_reason": str(exc)}},
        )
        return (
            jsonify(
                {
                    "error": "Message saved, but email delivery failed.",
                    "detail": str(exc),
                }
            ),
            503,
        )

    if not sent:
        contact_submissions.update_one(
            {"_id": inserted.inserted_id},
            {"$set": {"status": "failed", "failure_reason": reason}},
        )
        return (
            jsonify({"error": "Message saved, but email delivery is not configured.", "detail": reason}),
            503,
        )

    return jsonify({"message": "Thanks. Your message was sent successfully."}), 200
