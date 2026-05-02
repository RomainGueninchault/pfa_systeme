"""Exercise history tracking module.

Manages persistent storage of exercise completion status, including started,
failed, and completed exercises with optional completion times.
"""
import os
import yaml

HISTORY_FILE = os.path.expanduser("~/.trainer/history.yml")


def _load() -> dict:
    """Load exercise history from the history file.
    
    Returns:
        dict: The loaded history data, or empty dict if file doesn't exist or on error.
    """
    if not os.path.isfile(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception:
        return {}

def _save(data: dict):
    """Save exercise history to the history file.
    
    Args:
        data: Dictionary containing exercise history to save.
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def record_started(alias: str):
    """Record that an exercise has been started."""
    data = _load()
    data[alias] = {"status": "started"}
    _save(data)

def record_done(alias: str, time_str: str | None = None):
    """Record that an exercise has been completed successfully."""
    data = _load()
    entry = {"status": "done"}
    if time_str is not None:
        entry["time"] = time_str
    data[alias] = entry
    _save(data)

def record_failed(alias: str):
    """Record that an exercise was attempted but failed."""
    data = _load()
    # only overwrite if not already done
    if data.get(alias, {}).get("status") != "done":
        data[alias] = {"status": "failed"}
    _save(data)

def get_status(alias: str) -> dict | None:
    """Return a dict with the status and info of an exercise.
    
    Return:
    - None if no history
    - {"status": "started"} if started
    - {"status": "failed"} if attempted but failed
    - {"status": "done", "time": "time_str"} if successful (time can be None)
    """
    data = _load()
    entry = data.get(alias)
    if entry is None:
        return None
    return entry

