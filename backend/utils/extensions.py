"""
CareerAI — Shared Flask Extensions

Bcrypt and JWTManager are instantiated here (unbound) and initialized
inside the app factory with .init_app(app). Routes import them from this
module, which prevents circular imports between app.py and blueprints.
"""

from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(get_remote_address, storage_uri="memory://")
