from pathlib import Path

from flask import Flask

from .config import Config
from .extensions import db, login_manager, socketio
from .security import register_security


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    cors_origins = app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS")
    if cors_origins and "," in cors_origins:
        cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    socketio.init_app(app, cors_allowed_origins=cors_origins)
    register_security(app)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .rooms.routes import rooms_bp
    from .tasks.routes import tasks_bp
    from .files.routes import files_bp
    from .admin.routes import admin_bp
    from .rooms import socket_events

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(rooms_bp, url_prefix="/rooms")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(files_bp, url_prefix="/files")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    socket_events.register_events(socketio)

    return app
