import os
import yaml
from history import get_status

CFG = ("config.yml", "config.yaml")
INDEX = ".trainer_index.yml"

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
ORANGE  = "\033[38;5;208m"

def get_exercise_status(ex_dir):
    """Retourne le statut de l'exercice : (status, time).
    
    Status peut être:
    - 'not_started' : pas d'historique
    - 'started' : commencé mais pas réussi/échoué
    - 'failed' : tenté mais échoué
    - 'done_in_time' : réussi dans le temps imparti
    - 'done_overtime' : réussi mais dépassement du temps
    """
    entry = get_status(ex_dir)
    
    if entry is None:
        return ('not_started', None)
    
    status = entry.get('status')
    time_str = entry.get('time')
    
    if status == 'done':
        if time_str is None:
            return ('done_overtime', time_str)
        return ('done_in_time', time_str)
    elif status == 'failed':
        return ('failed', None)
    elif status == 'started':
        return ('started', None)
    
    return ('not_started', None)

def get_status_color(status):
    """Retourne la couleur ANSI pour un statut donné."""
    color_map = {
        'not_started': BLUE,
        'started': YELLOW,
        'failed': RED,
        'done_in_time': GREEN,
        'done_overtime': ORANGE,
    }
    return color_map.get(status, BLUE)

def yml(pathFile):
    try:
        with open(pathFile, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

# we work with tree logic for DB    
def leaf(dirpath):
    try:
        for name in os.listdir(dirpath):
            if os.path.isdir(os.path.join(dirpath, name)):
                return False
        return True
    except Exception:
        return False

def exName(pathFile):
    c = yml(pathFile)
    n = c.get("name")
    if isinstance(n, str) and n.strip():
        return n.strip()
    return os.path.basename(os.path.dirname(pathFile))

def nonempty(label, v):
    if v is None: return
    if isinstance(v, str) and not v.strip(): return
    if isinstance(v, (list, dict)) and not v: return
    print(f"{label}: {v}")

def tags_norm(v):
    if v is None: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s: return []
    return [t.strip() for t in s.split(",")] if "," in s else s.split()

def rebuild_index(base_dir):
    root = os.path.expanduser(base_dir)
    
    found = [] 
    for repo_name in sorted(os.listdir(root)):
        repo_path = os.path.join(root, repo_name)
        if not os.path.isdir(repo_path):
            continue

        for dirpath, dirnames, filenames in os.walk(repo_path):
            # ignore config à la racine du repo
            if dirpath == repo_path:
                continue

            cfg_file = None
            for fn in CFG:
                if fn in filenames:
                    cfg_file = os.path.join(dirpath, fn)
                    break
            if not cfg_file:
                continue

            if not leaf(dirpath):
                continue

            found.append((exName(cfg_file), os.path.realpath(dirpath)))

    groups = {}
    for name, path in found:
        groups.setdefault(name, set()).add(path)

    exercises = {}
    for name in sorted(groups):
        paths = sorted(groups[name])  # ordre stable
        for i, p in enumerate(paths):
            alias = name if i == 0 else f"{name}_{i}"
            exercises[alias] = p

    data = {"version": 1, "exercises": exercises}
    out_path = os.path.join(root, INDEX)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    return out_path

def read_index(base_dir):
    root = os.path.expanduser(base_dir)
    p = os.path.join(root, INDEX)
    if not os.path.isfile(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def lsRun(args):
    idx = read_index(args.base_dir)
    exercises = (idx.get("exercises") if isinstance(idx, dict) else {}) or {}

    if not exercises:
        print(RED + "Index absent/vidé. Lance d'abord: trainer import <url> (qui rebuild l'index)." + RESET)
        return

    tf = (args.tag or "").strip().lower()
    use_color = getattr(args, 'color', False)
    hide_done = getattr(args, 'done', False)

    rows = []

    for alias in sorted(exercises):
        ex_dir = exercises[alias]
        cfg = os.path.join(ex_dir, "config.yml")
        if not os.path.isfile(cfg):
            cfg2 = os.path.join(ex_dir, "config.yaml")
            if not os.path.isfile(cfg2):
                continue
            cfg = cfg2

        c = yml(cfg)
        tags = tags_norm(c.get("tags"))
        tags_str = " ".join(tags)

        if tf and tf not in tags_str.lower():
            continue

        # Récupérer le statut de l'exercice
        ex_status, ex_time = get_exercise_status(ex_dir)
        
        # Par défaut, ignorer les exercices réussis (sauf si -d activé)
        if not hide_done and ex_status in ('done_in_time', 'done_overtime'):
            continue

        desc = c.get("description") or ""

        rows.append((alias, tags_str, desc, ex_status, ex_time))

    if not rows:
        print(RED + "No exercises found." + RESET)
        return
    
    name_w = max(len(r[0]) for r in rows)
    tags_w = max(len(r[1]) for r in rows)

    name_w = max(name_w, len("NAME"))
    tags_w = max(tags_w, len("TAGS"))

    header = (GREEN + "NAME".ljust(name_w) + RESET + "   " + CYAN + "TAGS".ljust(tags_w) + RESET + "   " + MAGENTA + "DESCRIPTION" + RESET)

    print(header)
    print("-" * (name_w + tags_w + 65))

    for name, tags, desc, status, time_info in rows:
        if use_color:
            color = get_status_color(status)
            print(color + name.ljust(name_w) + RESET + "   " + tags.ljust(tags_w) + "   " + desc)
        else:
            print(BLUE + name.ljust(name_w) + RESET + "   " + tags.ljust(tags_w) + "   " + desc)
