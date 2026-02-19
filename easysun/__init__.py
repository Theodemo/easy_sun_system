import os

from flask import Flask

from config import Config


def create_app(config_overrides=None):
    """Flask application factory."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )

    # Load default config
    app.config.from_object(Config)

    # Apply overrides (e.g., from CLI arguments)
    if config_overrides:
        app.config.update(config_overrides)

    # Initialize database
    from .database.db import init_app as init_db

    init_db(app)

    # Register blueprints
    from .routes.pages import pages_bp
    from .routes.api import api_bp
    from .routes.system import system_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(system_bp, url_prefix="/api")

    # Initialize register reader (real or simulated)
    from .services.reader import init_reader

    init_reader(app)

    # In simulation mode, seed the database with historical data
    if app.config.get("SIMULATION_MODE"):
        from .database.repository import seed_simulation_data

        seed_simulation_data(
            app.config["DATABASE_PATH"],
            days=3,
            peak_w=app.config.get("SIM_PANEL_PEAK_W", 3000),
        )

    # Start background tasks
    from .tasks.scheduler import start_scheduler

    start_scheduler(app)

    return app
