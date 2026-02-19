from datetime import datetime
from unittest.mock import patch

from easysun.services.simulator import SolarSimulator


def make_simulator(**kwargs):
    config = {
        "SIM_PANEL_PEAK_W": 3000,
        "SIM_BATTERY_CAPACITY_WH": 4800,
        "SIM_BATTERY_VOLTAGE_NOMINAL": 48.0,
        "SIM_LATITUDE": 43.6,
    }
    config.update(kwargs)
    return SolarSimulator(config)


class TestSolarCurve:
    def test_night_zero(self):
        sim = make_simulator()
        # 2:00 AM in winter
        with patch("easysun.services.simulator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 1, 15, 2, 0)
            data = sim.read_all_display()
        assert data["chargw"] == 0
        assert data["pvv"] == 0

    def test_midday_positive(self):
        sim = make_simulator()
        with patch("easysun.services.simulator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 7, 15, 12, 30)
            data = sim.read_all_display()
        assert data["chargw"] > 0

    def test_summer_higher_than_winter(self):
        sim_summer = make_simulator()
        sim_winter = make_simulator()

        with patch("easysun.services.simulator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 7, 15, 12, 30)
            data_summer = sim_summer.read_all_display()

        with patch("easysun.services.simulator.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 1, 15, 12, 30)
            data_winter = sim_winter.read_all_display()

        assert data_summer["chargw"] > data_winter["chargw"]


class TestBattery:
    def test_soc_bounds(self):
        sim = make_simulator()
        # SOC should always be between 10 and 100
        for _ in range(50):
            data = sim.read_all_display()
            assert 10.0 <= data["batsoc"] <= 100.0

    def test_voltage_range(self):
        sim = make_simulator()
        data = sim.read_all_display()
        assert 44.0 <= data["batv"] <= 56.4


class TestLoadSimulation:
    def test_load_positive(self):
        sim = make_simulator()
        data = sim.read_all_display()
        assert data["loadw"] > 0

    def test_load_percent_positive(self):
        sim = make_simulator()
        data = sim.read_all_display()
        assert data["loadpcent"] >= 0


class TestReadForStorage:
    def test_returns_expected_keys(self):
        sim = make_simulator()
        data = sim.read_for_storage()
        assert "CHARGW" in data
        assert "LOADW" in data

    def test_values_are_numbers(self):
        sim = make_simulator()
        data = sim.read_for_storage()
        assert isinstance(data["CHARGW"], (int, float))
        assert isinstance(data["LOADW"], (int, float))
