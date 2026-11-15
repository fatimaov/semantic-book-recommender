from flask import Flask

from . import models
from .config import Config
from .extensions import cors, db, migrate
from .routes import blueprints


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app
