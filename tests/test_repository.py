import sqlite3
import time
import os
import tempfile

import pytest

from easysun.database.repository import (
    save_register_value,
    query_register_values,
    compute_energy_kwh,
    clear_old_data,
    clear_all_data,
)


@pytest.fixture
def db_path():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    with sqlite3.connect(path) as conn:
        conn.execute(
            """CREATE TABLE registers
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp INTEGER NOT NULL)"""
        )
        conn.execute(
            """CREATE INDEX idx_registers_name_ts
               ON registers(name, timestamp)"""
        )
    yield path
    try:
        os.unlink(path)
    except PermissionError:
        pass  # Windows may still hold the file lock


class TestSaveRegisterValue:
    def test_save_and_query(self, db_path):
        save_register_value(db_path, "CHARGW", 1500.0)
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("SELECT name, value FROM registers").fetchone()
        assert row[0] == "CHARGW"
        assert row[1] == 1500.0


class TestQueryRegisterValues:
    def test_query_range(self, db_path):
        now = int(time.time())
        with sqlite3.connect(db_path) as conn:
            for i in range(5):
                conn.execute(
                    "INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
                    ("CHARGW", 100.0 * (i + 1), now + i * 60),
                )

        values, timestamps, total = query_register_values(
            db_path, "CHARGW", now - 1, now + 300
        )
        assert len(values) == 5
        assert len(timestamps) == 5
        assert values[0] == 100.0
        assert values[4] == 500.0

    def test_empty_range(self, db_path):
        values, timestamps, total = query_register_values(
            db_path, "CHARGW", 0, 1
        )
        assert values == []
        assert timestamps == []
        assert total == 0.0


class TestComputeEnergyKwh:
    def test_constant_power(self):
        # 1000W for 1 hour = 1 kWh
        power = [1000.0, 1000.0]
        times = [0, 3600]
        assert compute_energy_kwh(power, times) == 1.0

    def test_linear_ramp(self):
        # 0W to 2000W over 1 hour (trapezoidal avg = 1000W) = 1 kWh
        power = [0.0, 2000.0]
        times = [0, 3600]
        assert compute_energy_kwh(power, times) == 1.0

    def test_single_point(self):
        assert compute_energy_kwh([1000.0], [0]) == 0.0

    def test_empty(self):
        assert compute_energy_kwh([], []) == 0.0


class TestClearData:
    def test_clear_old(self, db_path):
        now = int(time.time())
        old_ts = now - 400 * 86400  # 400 days ago
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
                ("CHARGW", 100.0, old_ts),
            )
            conn.execute(
                "INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
                ("CHARGW", 200.0, now),
            )

        clear_old_data(db_path, 365)

        with sqlite3.connect(db_path) as conn:
            rows = conn.execute("SELECT * FROM registers").fetchall()
        assert len(rows) == 1

    def test_clear_all(self, db_path):
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "INSERT INTO registers (name, value, timestamp) VALUES (?, ?, ?)",
                ("CHARGW", 100.0, int(time.time())),
            )
        clear_all_data(db_path)
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute("SELECT * FROM registers").fetchall()
        assert len(rows) == 0
