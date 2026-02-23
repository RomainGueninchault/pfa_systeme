from pathlib import Path
import hashlib, yaml
import base64

CFG = ("config.yml", "config.yaml")

def yml(p):
    try:
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

# Pour afficher les champs de config.yml seulement celles non vide    
def nonempty(label, v):
    if v is None: return
    if isinstance(v, str) and not v.strip(): return
    if isinstance(v, (list, dict)) and not v: return
    print(f"{label}: {v}")

# valable seulement dans ce modele: base -> base* & config | files & config    
def leaf(d):
    try:
        return not any(x.is_dir() for x in d.iterdir())
    except Exception:
        return False
    

def base_name(base):
    for f in CFG:
        p = base / f
        if p.is_file():
            n = yml(p).get("name")
            if isinstance(n, str) and n.strip():
                return n.strip()
    return base.name

# unifier les tags dans un array pour simplifier
def tags_norm(v):
    if v is None: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s: return []
    return [t.strip() for t in s.split(",")] if "," in s else s.split()


# Convert chemin d'exercice en base64
def codage(ex_dir, root):
    key = ex_dir.relative_to(root).as_posix()
    return base64.urlsafe_b64encode(key.encode()).decode()

# la fct principale
def lsRun(args):
    root = Path(args.base_dir).expanduser()
    if not root.exists():
        print("Base directory does not exist, try at least trainer -import <url> once"); return

    tf = (args.tag or "").strip().lower()

    for base in sorted([p for p in root.iterdir() if p.is_dir()]):
        bdisp = base_name(base)
        for fn in CFG:
            for cfg in base.rglob(fn):
                if cfg.parent == base: 
                    continue
                ex_dir = cfg.parent
                if not leaf(ex_dir):
                    continue

                c = yml(cfg)
                ex = c.get("name")
                ex = ex.strip() if isinstance(ex, str) and ex.strip() else ex_dir.name

                tags = tags_norm(c.get("tags"))
                if tf and tf not in " ".join(t.lower() for t in tags):
                    continue

                print("-" * 30)
                nonempty("Base", bdisp)
                nonempty("Exercise", ex)
                nonempty("Hash", codage(ex_dir, root))
                nonempty("Author", c.get("author"))
                nonempty("Langage", c.get("langage"))
                nonempty("Tags", tags)
                nonempty("Description", c.get("description"))
