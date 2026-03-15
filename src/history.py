import os
import base64
import hashlib
import yaml

HISTORY_FILE = os.path.expanduser("~/.trainer/history.yml")

def _b64hash(value: str) -> str:
    """Retourne un hash base64 url-safe court (8 chars) d'une chaîne."""
    digest = hashlib.sha256(value.encode()).digest()
    return base64.urlsafe_b64encode(digest)[:8].decode()

def exo_hash(exo_path: str) -> str:
    """Hash du chemin complet de l'exercice depuis ~"""
    return _b64hash(os.path.realpath(os.path.expanduser(exo_path)))


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

def record_started(exo_path: str):
    """Enregistre qu'un exercice a été commencé."""
    data = _load()
    h_exo = exo_hash(exo_path)
    data[h_exo] = {"status": "started"}
    _save(data)

def record_done(exo_path: str, time_str: str | None = None):
    """Enregistre qu'un exercice a été réussi."""
    data = _load()
    h_exo = exo_hash(exo_path)
    entry = {"status": "done"}
    if time_str is not None:
        entry["time"] = time_str
    data[h_exo] = entry
    _save(data)

def record_failed(exo_path: str):
    """Enregistre qu'un exercice a été tenté mais raté."""
    data = _load()
    h_exo = exo_hash(exo_path)
    # on écrase seulement si pas déjà done
    if data.get(h_exo, {}).get("status") != "done":
        data[h_exo] = {"status": "failed"}
    _save(data)

def get_status(exo_path: str) -> str | None:
    """Retourne le statut d'un exercice : 'started', 'done', 'failed', ou None."""
    data = _load()
    h_exo = exo_hash(exo_path)
    entry = data.get(h_exo)
    if entry is None:
        return None
    return entry.get("status")

