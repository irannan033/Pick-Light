"""
Hardware adapter for the Pick-to-Light system.

This file is intentionally a simulator. Replace these functions with calls to your
actual PLC/ESP32/controller protocol only after validating hardware behavior.
"""
from threading import Lock

_lock = Lock()
_light_states = {}

def activate_light(bin_id: str, low_stock: bool = False):
    """Simulate activating a bin indicator."""
    with _lock:
        _light_states[bin_id] = "BLINKING_LOW_STOCK" if low_stock else "ON"
    return _light_states[bin_id]

def confirm_button(bin_id: str):
    """Simulate a physical push-button confirmation."""
    with _lock:
        _light_states[bin_id] = "CONFIRMED"
    return True

def turn_off_light(bin_id: str):
    with _lock:
        _light_states[bin_id] = "OFF"

def get_light_state(bin_id: str):
    with _lock:
        return _light_states.get(bin_id, "OFF")
