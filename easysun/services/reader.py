from abc import ABC, abstractmethod


class RegisterReader(ABC):
    """Abstract interface for reading solar system registers."""

    @abstractmethod
    def read_all_display(self):
        """Read all registers needed for real-time display.

        Returns dict with keys: pvv, chargw, batv, batsoc, loadw, loadpcent
        """

    @abstractmethod
    def read_for_storage(self):
        """Read registers that need to be persisted.

        Returns dict with keys: CHARGW, LOADW
        """


def init_reader(app):
    """Factory: attach the appropriate reader to the app."""
    if app.config.get("SIMULATION_MODE", False):
        from .simulator import SolarSimulator

        app.extensions["register_reader"] = SolarSimulator(app.config)
    else:
        from .modbus_service import ModbusReader

        app.extensions["register_reader"] = ModbusReader(app.config)


def get_reader(app):
    """Get the register reader from the app."""
    return app.extensions["register_reader"]
