"""
CareerAI — Flask Application Entry Point
AI-Driven Personalized Career Guidance System

Creates the Flask app, wires CORS / JWT / Bcrypt, connects MongoDB Atlas,
registers all feature blueprints, and exposes consistent JSON error handling.
"""

import os
import logging

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import Config
from database import init_indexes, ping
from utils.extensions import bcrypt, jwt, limiter

from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.resume_routes import resume_bp
from routes.career_routes import career_bp
from routes.roadmap_routes import roadmap_bp
from routes.analytics_routes import analytics_bp
from routes.contact_routes import contact_bp
from routes.intelligence_routes import intelligence_bp


def create_app():
    """Application factory: build and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the resume upload directory exists before any request.
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # ------------------------------------------------------------------
    # Extensions
    # ------------------------------------------------------------------
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # ------------------------------------------------------------------
    # Structured logging
    # ------------------------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # ------------------------------------------------------------------
    # spaCy model check
    # ------------------------------------------------------------------
    import spacy
    try:
        spacy.load("en_core_web_sm")
        logging.info("spaCy model en_core_web_sm loaded successfully.")
    except OSError:
        logging.warning(
            "spaCy model 'en_core_web_sm' is NOT installed. "
            "Resume skill extraction will fail. "
            "Fix: python -m spacy download en_core_web_sm"
        )

    # ------------------------------------------------------------------
    # Database indexes (safe to call on every boot — idempotent)
    # ------------------------------------------------------------------
    init_indexes()

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")
    app.register_blueprint(resume_bp, url_prefix="/api/resume")
    app.register_blueprint(career_bp, url_prefix="/api/career")
    app.register_blueprint(roadmap_bp, url_prefix="/api/roadmap")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")
    app.register_blueprint(intelligence_bp, url_prefix="/api/intelligence")

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        db_ok = ping()
        status_code = 200 if db_ok else 503
        return jsonify({
            "status": "ok" if db_ok else "degraded",
            "service": "careerai-backend",
            "mongodb": "connected" if db_ok else "unreachable",
        }), status_code

    # ------------------------------------------------------------------
    # JWT error responses (consistent JSON instead of default HTML)
    # ------------------------------------------------------------------
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Authentication required.", "detail": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Invalid authentication token.", "detail": reason}), 401

    @jwt.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return jsonify({"error": "Session expired. Please log in again."}), 401

    # ------------------------------------------------------------------
    # Request logging
    # ------------------------------------------------------------------
    @app.before_request
    def log_request():
        logging.info("%s %s", request.method, request.path)

    @app.after_request
    def log_response(response):
        logging.info("%s %s → %s", request.method, request.path, response.status_code)
        return response

    # ------------------------------------------------------------------
    # Global error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request."}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({"error": "File too large. Maximum size is 5 MB."}), 413

    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    @app.errorhandler(500)
    def internal_error(error):
        logging.exception("Internal server error")
        return jsonify({"error": "Internal server error. Please try again."}), 500

    # ------------------------------------------------------------------
    # Serve Frontend (static HTML/CSS/JS)
    # In production, build.sh copies frontend files to backend/static/
    # In local dev, we also check ../frontend/ for convenience
    # ------------------------------------------------------------------
    BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BACKEND_DIR, "static")
    FRONTEND_DIR = os.path.join(BACKEND_DIR, "..", "frontend")

    def _get_frontend_dir():
        """Return the best available frontend directory."""
        if os.path.isdir(STATIC_DIR) and os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
            return STATIC_DIR
        if os.path.isdir(FRONTEND_DIR) and os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
            return FRONTEND_DIR
        return STATIC_DIR

    @app.route("/")
    def serve_index():
        return send_from_directory(_get_frontend_dir(), "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        fdir = _get_frontend_dir()
        file_path = os.path.join(fdir, path)
        if os.path.isfile(file_path):
            return send_from_directory(fdir, path)
        return send_from_directory(fdir, "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
