import os
import yaml

CFG = ("config.yml", "config.yaml")
INDEX = ".trainer_index.yml"

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
        print("Index absent/vidé. Lance d'abord: trainer import <url> (qui rebuild l'index).")
        return

    tf = (args.tag or "").strip().lower()

    for alias in sorted(exercises):
        ex_dir = exercises[alias]
        cfg = os.path.join(ex_dir, "config.yml")
        if not os.path.isfile(cfg):
            # si l'exercice utilise config.yaml, tu peux aussi tester ça:
            cfg2 = os.path.join(ex_dir, "config.yaml")
            if not os.path.isfile(cfg2):
                continue
            cfg = cfg2

        c = yml(cfg)
        tags = tags_norm(c.get("tags"))

        if tf and tf not in " ".join(t.lower() for t in tags):
            continue

        print("-" * 30)
        nonempty("Exercise", alias)
        nonempty("Tags", tags)
        nonempty("Description", c.get("description"))
