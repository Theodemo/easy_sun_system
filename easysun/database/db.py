import sqlite3

from flask import g, current_app


def get_db():
    """Get a database connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create tables and indexes if they don't exist."""
    with sqlite3.connect(app.config["DATABASE_PATH"]) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS registers
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp INTEGER NOT NULL)"""
        )
        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_registers_name_ts
               ON registers(name, timestamp)"""
        )


def init_app(app):
    """Initialize database for the Flask app."""
    init_db(app)
    app.teardown_appcontext(close_db)
