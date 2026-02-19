import sqlite3
import math
import random
import time
from datetime import datetime, timedelta


def save_register_value(db_path, register_name, value):
    """Save a register value with current timestamp."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
            (register_name, value, int(time.time())),
        )


def query_register_values(db_path, register_name, start_ts, end_ts):
    """Query register values in a time range.

    Returns (values, timestamps, total_kwh).
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT value, timestamp FROM registers "
            "WHERE name = ? AND timestamp BETWEEN ? AND ? "
            "ORDER BY timestamp",
            (register_name, start_ts, end_ts),
        ).fetchall()

    values = [r["value"] for r in rows]
    timestamps = [r["timestamp"] for r in rows]
    total_kwh = compute_energy_kwh(values, timestamps)
    return values, timestamps, total_kwh


def compute_energy_kwh(power_watts, times_sec):
    """Trapezoidal integration of power over time to get energy in kWh."""
    if len(power_watts) < 2:
        return 0.0

    energy_joules = 0.0
    for i in range(1, len(power_watts)):
        dt = times_sec[i] - times_sec[i - 1]
        avg_power = (power_watts[i] + power_watts[i - 1]) / 2.0
        energy_joules += avg_power * dt

    return round(energy_joules / 3_600_000.0, 2)


def clear_old_data(db_path, retention_days):
    """Delete records older than retention_days."""
    cutoff = int(time.time()) - (retention_days * 86400)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM registers WHERE timestamp < ?", (cutoff,))


def clear_all_data(db_path):
    """Delete all records and vacuum the database."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DELETE FROM registers")
        conn.commit()
        conn.execute("VACUUM")
    finally:
        conn.close()


def seed_simulation_data(db_path, days=3, interval_sec=180, peak_w=3000):
    """Pre-populate the database with realistic simulated data.

    Generates data points every `interval_sec` seconds for the last `days` days.
    Only runs if the database is empty.
    """
    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM registers").fetchone()[0]
        if count > 0:
            return  # Database already has data

    now = datetime.now()
    start = now - timedelta(days=days)
    cloud_factor = 1.0
    cloud_change_step = 0
    load_extra = 0.0
    load_change_step = 0

    rows = []
    current = start
    step = 0

    while current <= now:
        ts = int(current.timestamp())
        hour = current.hour + current.minute / 60.0
        day_of_year = current.timetuple().tm_yday

        # Solar production (Gaussian bell curve)
        seasonal = 0.6 + 0.4 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        sigma = 2.0 + 1.5 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        solar = peak_w * seasonal * math.exp(-((hour - 12.5) ** 2) / (2 * sigma ** 2))

        # Cloud cover (changes every ~10 steps = 30 min)
        if step - cloud_change_step > random.randint(8, 15):
            target = random.uniform(0.3, 1.0)
            cloud_factor += (target - cloud_factor) * 0.3
            cloud_change_step = step
        solar *= cloud_factor

        # Night
        if hour < 5.5 or hour > 21.0:
            solar = 0.0

        solar *= 1.0 + random.uniform(-0.03, 0.03)
        solar = max(0.0, round(solar, 0))

        # Load (base + variable)
        if step - load_change_step > random.randint(5, 20):
            load_extra = random.uniform(0, 800)
            load_change_step = step
        load = round(200.0 + load_extra + random.uniform(-10, 10), 0)

        rows.append(("CHARGW", solar, ts))
        rows.append(("LOADW", load, ts))

        current += timedelta(seconds=interval_sec)
        step += 1

    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
            rows,
        )
