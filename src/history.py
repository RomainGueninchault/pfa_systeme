import os
import yaml

HISTORY_FILE = os.path.expanduser("~/.trainer/history.yml")


def _load() -> dict:
    if not os.path.isfile(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception:
        return {}

def _save(data: dict):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def record_started(alias: str):
    """Enregistre qu'un exercice a été commencé."""
    data = _load()
    data[alias] = {"status": "started"}
    _save(data)

def record_done(alias: str, time_str: str | None = None):
    """Enregistre qu'un exercice a été réussi."""
    data = _load()
    entry = {"status": "done"}
    if time_str is not None:
        entry["time"] = time_str
    data[alias] = entry
    _save(data)

def record_failed(alias: str):
    """Enregistre qu'un exercice a été tenté mais raté."""
    data = _load()
    # on écrase seulement si pas déjà done
    if data.get(alias, {}).get("status") != "done":
        data[alias] = {"status": "failed"}
    _save(data)

def get_status(alias: str) -> dict | None:
    """Retourne un dict avec le statut et les infos d'un exercice.
    
    Retour:
    - None si pas d'historique
    - {"status": "started"} si commencé
    - {"status": "failed"} si tenté mais raté
    - {"status": "done", "time": "time_str"} si réussi (time peut être None)
    """
    data = _load()
    entry = data.get(alias)
    if entry is None:
        return None
    return entry

