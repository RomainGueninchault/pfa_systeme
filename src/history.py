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

def dir_hash(dir_path: str) -> str:
    return _b64hash(os.path.realpath(dir_path))

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

def record_started(exo_path: str, work_dir: str):
    """Enregistre qu'un exercice a été commencé dans work_dir."""
    data = _load()
    h_exo = exo_hash(exo_path)
    h_dir = dir_hash(work_dir)
    data[h_exo] = {"status": "started", "dir": h_dir}
    _save(data)

def record_done(exo_path: str, work_dir: str):
    """Enregistre qu'un exercice a été réussi."""
    data = _load()
    h_exo = exo_hash(exo_path)
    h_dir = dir_hash(work_dir)
    data[h_exo] = {"status": "done", "dir": h_dir}
    _save(data)

def record_failed(exo_path: str, work_dir: str):
    """Enregistre qu'un exercice a été tenté mais raté."""
    data = _load()
    h_exo = exo_hash(exo_path)
    h_dir = dir_hash(work_dir)
    # on écrase seulement si pas déjà done
    if data.get(h_exo, {}).get("status") != "done":
        data[h_exo] = {"status": "failed", "dir": h_dir}
    _save(data)

def record_clean(exo_path: str):
    """Supprime le hash du répertoire après clean, garde juste le statut."""
    data = _load()
    h_exo = exo_hash(exo_path)
    if h_exo in data:
        entry = data[h_exo]
        entry.pop("dir", None)
        data[h_exo] = entry
    _save(data)

def get_status(exo_path: str) -> str | None:
    """Retourne le statut d'un exercice : 'started', 'done', 'failed', ou None."""
    data = _load()
    h_exo = exo_hash(exo_path)
    entry = data.get(h_exo)
    if entry is None:
        return None
    return entry.get("status")

