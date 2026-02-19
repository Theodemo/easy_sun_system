import math
import time
import random
import threading
from datetime import datetime

from .reader import RegisterReader


class SolarSimulator(RegisterReader):
    """Realistic solar power plant simulator.

    Simulates:
    - Solar production with a Gaussian bell curve varying by season
    - Variable load consumption
    - Battery charge/discharge based on energy balance
    - Cloud cover with slow random variations
    """

    def __init__(self, config):
        self._lock = threading.Lock()

        # Constants from config
        self._peak_w = config.get("SIM_PANEL_PEAK_W", 3000)
        self._bat_capacity_wh = config.get("SIM_BATTERY_CAPACITY_WH", 4800)
        self._bat_v_nominal = config.get("SIM_BATTERY_VOLTAGE_NOMINAL", 48.0)
        self._latitude = config.get("SIM_LATITUDE", 43.6)

        # Mutable state
        self._battery_soc = 60.0  # Start at 60%
        self._current_load_extra = 0.0
        self._load_change_time = 0.0
        self._cloud_factor = 1.0
        self._cloud_change_time = 0.0
        self._last_update_time = time.time()

    def _get_solar_power(self, now):
        """Compute solar production using a Gaussian bell curve."""
        hour = now.hour + now.minute / 60.0
        day_of_year = now.timetuple().tm_yday

        # Seasonal variation: higher production in summer
        seasonal_factor = 0.6 + 0.4 * math.sin(
            2 * math.pi * (day_of_year - 80) / 365
        )

        # Daylight width varies by season (wider in summer)
        sigma = 2.0 + 1.5 * math.sin(2 * math.pi * (day_of_year - 80) / 365)

        solar_noon = 12.5  # France is ~30min west of timezone center

        # Gaussian curve
        power = (
            self._peak_w
            * seasonal_factor
            * math.exp(-((hour - solar_noon) ** 2) / (2 * sigma**2))
        )

        # Apply cloud cover
        power *= self._get_cloud_factor()

        # Night time
        if hour < 5.5 or hour > 21.0:
            power = 0.0

        # Small noise +/- 3%
        power *= 1.0 + random.uniform(-0.03, 0.03)

        return max(0.0, power)

    def _get_cloud_factor(self):
        """Slowly varying cloud cover (changes every 5-30 minutes)."""
        current_time = time.time()
        if current_time - self._cloud_change_time > random.uniform(300, 1800):
            target = random.uniform(0.3, 1.0)
            self._cloud_factor += (target - self._cloud_factor) * 0.3
            self._cloud_change_time = current_time
        return self._cloud_factor

    def _get_load_power(self):
        """Base load + random step changes every 5-30 minutes."""
        current_time = time.time()
        if current_time - self._load_change_time > random.uniform(300, 1800):
            self._current_load_extra = random.uniform(0, 800)
            self._load_change_time = current_time
        base = 200.0
        return base + self._current_load_extra + random.uniform(-10, 10)

    def _update_battery(self, solar_w, load_w, dt_seconds):
        """Update battery SOC based on energy balance."""
        net_w = solar_w - load_w
        energy_wh = (net_w * dt_seconds) / 3600.0
        soc_change = (energy_wh / self._bat_capacity_wh) * 100.0
        self._battery_soc = max(10.0, min(100.0, self._battery_soc + soc_change))

    def _battery_voltage(self):
        """Map SOC to voltage (linear approximation for 48V system)."""
        v_min, v_max = 44.0, 56.4
        return v_min + (v_max - v_min) * (self._battery_soc / 100.0)

    def read_all_display(self):
        with self._lock:
            now = datetime.now()
            current_time = time.time()
            dt = current_time - self._last_update_time
            self._last_update_time = current_time

            solar = self._get_solar_power(now)
            load = self._get_load_power()
            self._update_battery(solar, load, dt)

            bat_v = self._battery_voltage()
            pv_v = 85.0 + random.uniform(-5, 5) if solar > 0 else 0.0

            return {
                "pvv": round(pv_v, 2),
                "chargw": round(solar, 0),
                "batv": round(bat_v, 2),
                "batsoc": round(self._battery_soc, 0),
                "loadw": round(load, 0),
                "loadpcent": round((load / self._peak_w) * 100, 0),
            }

    def read_for_storage(self):
        with self._lock:
            now = datetime.now()
            current_time = time.time()
            dt = current_time - self._last_update_time
            self._last_update_time = current_time

            solar = self._get_solar_power(now)
            load = self._get_load_power()
            self._update_battery(solar, load, dt)

            return {
                "CHARGW": round(solar, 0),
                "LOADW": round(load, 0),
            }
