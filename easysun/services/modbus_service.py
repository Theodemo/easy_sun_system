import time
import threading
import logging

import minimalmodbus
from serial import SerialException

from .reader import RegisterReader
from ..models.registers import DISPLAY_REGISTERS, STORAGE_REGISTERS

logger = logging.getLogger(__name__)


class ModbusReader(RegisterReader):
    """Thread-safe Modbus register reader."""

    def __init__(self, config):
        self._lock = threading.Lock()
        self._instrument = None
        self._port = config.get("MODBUS_PORT", "/dev/ttyUSB0")
        self._slave_address = config.get("MODBUS_SLAVE_ADDRESS", 4)
        self._baudrate = config.get("MODBUS_BAUDRATE", 19200)
        self._timeout = config.get("MODBUS_TIMEOUT", 0.5)
        self._initialize()

    def _initialize(self):
        """Initialize the Modbus instrument with retry."""
        while True:
            with self._lock:
                try:
                    if self._instrument is not None:
                        self._instrument.serial.close()
                        self._instrument = None
                    time.sleep(2)
                    self._instrument = minimalmodbus.Instrument(
                        self._port, self._slave_address
                    )
                    self._instrument.serial.baudrate = self._baudrate
                    self._instrument.serial.timeout = self._timeout
                    logger.info("Modbus instrument initialized successfully")
                    return
                except Exception as e:
                    logger.error("Failed to initialize Modbus: %s", e)
                    if self._instrument is not None:
                        try:
                            self._instrument.serial.close()
                        except Exception:
                            pass
                        self._instrument = None
            time.sleep(60)

    def _read_register(self, address):
        """Read a single register. Returns raw value or None on error."""
        time.sleep(1)
        with self._lock:
            try:
                return self._instrument.read_registers(address, 1)[0]
            except (SerialException, Exception) as e:
                logger.error("Error reading register %d: %s", address, e)
                self._instrument = None

        # Reinitialize outside the lock
        self._initialize()
        return None

    def read_all_display(self):
        result = {}
        for key, reg_info in DISPLAY_REGISTERS.items():
            raw = self._read_register(reg_info["address"])
            if raw is not None:
                result[key] = round(raw * reg_info["mult_coef"], 2)
            else:
                result[key] = None
        return result

    def read_for_storage(self):
        result = {}
        for key, reg_info in STORAGE_REGISTERS.items():
            raw = self._read_register(reg_info["address"])
            if raw is not None:
                result[key] = raw
            else:
                result[key] = None
        return result
