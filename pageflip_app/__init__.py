import os
from flask import Flask
from .extensions import bcrypt, jwt, cors
from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.books import books_bp
from .routes.admin import admin_bp
from .config import Config


def create_app(config_class: type[Config] | None = None) -> Flask:
    app = Flask(__name__)

    # Config
    cfg_class = config_class or Config
    app.config.from_object(cfg_class())

    # Extensions
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", ["http://localhost:4200"])}})

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(admin_bp)

    return app
