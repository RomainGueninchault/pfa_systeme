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

# pour la recusivite
def find_cfg_in_dir(dirpath):
    for fn in CFG:
        p = os.path.join(dirpath, fn)
        if os.path.isfile(p):
            return p
    return None


def merge_tags(parent_value, child_value):
    merged = []
    seen = set()

    for tag in tags_norm(parent_value) + tags_norm(child_value):
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            merged.append(tag)

    return merged


def deep_merge(parent, child):
    """
    Fusion parent -> enfant.
    - dict + dict  => fusion récursive
    - tags         => concat + déduplication
    - sinon        => la valeur enfant écrase la valeur parent
    """
    if not isinstance(parent, dict):
        parent = {}
    if not isinstance(child, dict):
        child = {}

    result = dict(parent)

    for key, child_value in child.items():
        parent_value = result.get(key)

        if key == "tags":
            result[key] = merge_tags(parent_value, child_value)
        elif isinstance(parent_value, dict) and isinstance(child_value, dict):
            result[key] = deep_merge(parent_value, child_value)
        else:
            result[key] = child_value

    return result


def load_merged_config(ex_dir, base_dir):
    """
    Remonte depuis la feuille jusqu'à la racine du repo
    et fusionne tous les YAML trouvés.
    """
    root = os.path.realpath(os.path.expanduser(base_dir))
    ex_dir = os.path.realpath(ex_dir)

    rel_path = os.path.relpath(ex_dir, root)
    repo_name = rel_path.split(os.sep)[0]
    repo_root = os.path.join(root, repo_name)

    if not ex_dir.startswith(repo_root):
        return {}

    current = ex_dir
    stack = []

    while True:
        cfg = find_cfg_in_dir(current)
        if cfg:
            stack.append(cfg)

        if os.path.realpath(current) == os.path.realpath(repo_root):
            break

        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    merged = {}
    for cfg_path in reversed(stack):   # racine -> feuille
        merged = deep_merge(merged, yml(cfg_path))

    return merged


def get_exercise_status(alias):
    """Retourne le statut de l'exercice : (status, time).
    
    Status peut être:
    - 'not_started' : pas d'historique
    - 'started' : commencé mais pas réussi/échoué
    - 'failed' : tenté mais échoué
    - 'done_in_time' : réussi dans le temps imparti
    - 'done_overtime' : réussi mais dépassement du temps
    """
    entry = get_status(alias)

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
        'not_started': CYAN,
        'started': YELLOW,
        'failed': RED,
        'done_in_time': GREEN,
        'done_overtime': ORANGE,
    }
    return color_map.get(status, CYAN)

def get_repo_name(ex_dir, base_dir):
    """Extrait le nom du dépôt depuis le chemin de l'exercice.
    
    Retourne le nom du répertoire immédiatement après la base_dir.
    Ex: ~/.trainer/mon_repo/exercise -> mon_repo
    """
    root = os.path.expanduser(base_dir)
    rel_path = os.path.relpath(ex_dir, root)
    parts = rel_path.split(os.sep)
    return parts[0] if parts else ""

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

def exName(pathFile, base_dir=None):
    if base_dir is not None:
        ex_dir = os.path.dirname(pathFile)
        c = load_merged_config(ex_dir, base_dir)
    else:
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

            found.append((exName(cfg_file, base_dir=root), os.path.realpath(dirpath)))

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
    show_done = getattr(args, 'done', False)

    rows = []

    for alias in sorted(exercises):
        ex_dir = exercises[alias]
        cfg = os.path.join(ex_dir, "config.yml")
        if not os.path.isfile(cfg):
            cfg2 = os.path.join(ex_dir, "config.yaml")
            if not os.path.isfile(cfg2):
                continue
            cfg = cfg2

        c = load_merged_config(ex_dir, args.base_dir)
        tags = tags_norm(c.get("tags"))
        tags_str = " ".join(tags)

        if tf and tf not in tags_str.lower():
            continue

        # Récupérer le statut de l'exercice en utilisant l'alias
        ex_status, ex_time = get_exercise_status(alias)
        
        # Par défaut, ignorer les exercices réussis (sauf si -d activé)
        if not show_done and ex_status in ('done_in_time', 'done_overtime'):
            continue

        desc = c.get("description") or ""
        
        # Récupérer le nom du dépôt
        repo_name = get_repo_name(ex_dir, args.base_dir)

        rows.append((alias, tags_str, desc, ex_status, ex_time, repo_name))

    if not rows:
        print(RED + "No exercises found." + RESET)
        return
    
    name_w = max(len(r[0]) for r in rows)
    tags_w = max(len(r[1]) for r in rows)
    repo_w = max(len(r[5]) for r in rows)

    name_w = max(name_w, len("NAME"))
    tags_w = max(tags_w, len("TAGS"))
    repo_w = max(repo_w, len("REPO"))

    header = (GREEN + "NAME".ljust(name_w) + RESET + "     " + BLUE + "TAGS".ljust(tags_w) + RESET + "     " + ORANGE + "REPO".ljust(repo_w) + RESET + "     " + MAGENTA + "DESCRIPTION" + RESET)

    print(header)
    print("-" * (name_w + tags_w + repo_w + 95))

    for name, tags, desc, status, time_info, repo in rows:
        color = get_status_color(status)
        print(color + name.ljust(name_w) + RESET + "     " + tags.ljust(tags_w) + "     " + repo.ljust(repo_w) + "     " + desc)
