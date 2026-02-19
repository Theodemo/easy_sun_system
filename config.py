import os


class Config:
    # Mode
    SIMULATION_MODE = os.environ.get("EASYSUN_SIMULATION", "false").lower() == "true"

    # Modbus
    MODBUS_PORT = os.environ.get("EASYSUN_MODBUS_PORT", "/dev/ttyUSB0")
    MODBUS_SLAVE_ADDRESS = int(os.environ.get("EASYSUN_SLAVE_ADDR", "4"))
    MODBUS_BAUDRATE = int(os.environ.get("EASYSUN_BAUDRATE", "19200"))
    MODBUS_TIMEOUT = float(os.environ.get("EASYSUN_MODBUS_TIMEOUT", "0.5"))

    # Database
    DATABASE_PATH = os.environ.get(
        "EASYSUN_DB_PATH",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db"),
    )

    # Intervals (seconds)
    SAVE_INTERVAL = int(os.environ.get("EASYSUN_SAVE_INTERVAL", "180"))  # 3 minutes
    CLEAR_RETENTION_DAYS = int(os.environ.get("EASYSUN_RETENTION_DAYS", "365"))
    CLEAR_INTERVAL = int(os.environ.get("EASYSUN_CLEAR_INTERVAL", "86400"))  # 24h

    # Server
    HOST = os.environ.get("EASYSUN_HOST", "0.0.0.0")
    PORT = int(os.environ.get("EASYSUN_PORT", "80"))

    # Simulation parameters
    SIM_LATITUDE = float(os.environ.get("EASYSUN_SIM_LAT", "43.6"))
    SIM_PANEL_PEAK_W = int(os.environ.get("EASYSUN_SIM_PEAK_W", "3000"))
    SIM_BATTERY_CAPACITY_WH = int(os.environ.get("EASYSUN_SIM_BAT_WH", "4800"))
    SIM_BATTERY_VOLTAGE_NOMINAL = float(os.environ.get("EASYSUN_SIM_BAT_V", "48.0"))
