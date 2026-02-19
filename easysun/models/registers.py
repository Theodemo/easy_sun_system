import sys
import os

# Add project root to path so we can import config/registers.py
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_project_root, "config"))

from registers import registersMaps


def _get_reg(json_name):
    """Look up a register by its jsonName from the full register map."""
    for addr, info in registersMaps.items():
        if info[0] == json_name:
            return {
                "address": addr,
                "json_name": info[0],
                "reg_type": info[1],
                "display_name": info[2],
                "mult_coef": info[3],
                "unit": info[5],
            }
    raise KeyError(f"Register '{json_name}' not found in registersMaps")


# Registers needed for real-time display
DISPLAY_REGISTERS = {
    "pvv": _get_reg("PvV"),           # 15205, mult 0.1, V
    "chargw": _get_reg("ChargrW"),    # 15208, mult 1, W
    "batv": _get_reg("ChargrBatV"),   # 15206, mult 0.1, V
    "batsoc": _get_reg("BatSoc"),     # 25275, mult 1, %
    "loadw": _get_reg("LoadW"),       # 25215, mult 1, W
    "loadpcent": _get_reg("LoadPcent"),  # 25216, mult 1, %
}

# Registers persisted to the database every SAVE_INTERVAL
STORAGE_REGISTERS = {
    "CHARGW": _get_reg("ChargrW"),    # 15208
    "LOADW": _get_reg("LoadW"),       # 25215
}
