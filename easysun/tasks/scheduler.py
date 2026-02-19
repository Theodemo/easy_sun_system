import time
import threading
import logging

from ..services.reader import get_reader
from ..database.repository import save_register_value, clear_old_data

logger = logging.getLogger(__name__)


def _save_task(app):
    """Periodically read and save register values to the database."""
    with app.app_context():
        reader = get_reader(app)
        interval = app.config.get("SAVE_INTERVAL", 180)
        db_path = app.config["DATABASE_PATH"]

        while True:
            try:
                data = reader.read_for_storage()
                for name, value in data.items():
                    if value is not None:
                        save_register_value(db_path, name, value)
                logger.debug("Saved register values: %s", data)
            except Exception as e:
                logger.error("Error in save task: %s", e)
            time.sleep(interval)


def _clear_task(app):
    """Periodically clear old data beyond retention period."""
    with app.app_context():
        interval = app.config.get("CLEAR_INTERVAL", 86400)
        retention_days = app.config.get("CLEAR_RETENTION_DAYS", 365)
        db_path = app.config["DATABASE_PATH"]

        while True:
            try:
                clear_old_data(db_path, retention_days)
                logger.debug("Cleared data older than %d days", retention_days)
            except Exception as e:
                logger.error("Error in clear task: %s", e)
            time.sleep(interval)


def start_scheduler(app):
    """Start background save and clear tasks as daemon threads."""
    save_thread = threading.Thread(target=_save_task, args=(app,), daemon=True)
    clear_thread = threading.Thread(target=_clear_task, args=(app,), daemon=True)
    save_thread.start()
    clear_thread.start()
    logger.info("Background scheduler started")
