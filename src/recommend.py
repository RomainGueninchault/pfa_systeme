import os
import argparse
from typing import Any, Dict, List, Optional, Set

import yaml

from ls import read_index, tags_norm
from history import HISTORY_FILE, exo_hash

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"

CFG_NAMES = ("config.yml", "config.yaml")


def yml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

    
def find_config(exo_dir):
    for name in CFG_NAMES:
        path = os.path.join(exo_dir, name)
        if os.path.isfile(path):
            return path
    return None


# cfg est returne par yml sur config.yml
def parse_difficulty(cfg):
    value = cfg.get("difficulty")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_timeout_minutes(cfg):
    value = cfg.get("timeout")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

# return Dict[str, Dict[str, Any]] la premier str est le nom de l´ex et les autres sont les meta-donnes
def get_exercise_catalog(base_dir: str) -> Dict[str, Dict[str, Any]]:
    base_dir = os.path.expanduser(base_dir)
    idx = read_index(base_dir)
    exercises = (idx.get("exercises") if isinstance(idx, dict) else {}) or {}
    history = yml(HISTORY_FILE)

    catalog: Dict[str, Dict[str, Any]] = {}

    for alias, exo_dir in exercises.items():
        cfg_path = find_config(exo_dir)
        if not cfg_path:
            continue

        cfg = yml(cfg_path)
        tags = tags_norm(cfg.get("tags"))
        tags_set = {t.strip().lower() for t in tags if str(t).strip()}

        history_entry = history.get(exo_hash(exo_dir), {})
        status = history_entry.get("status")

        catalog[alias] = {
            "alias": alias,
            "path": exo_dir,
            "description": (cfg.get("description") or "").strip(),
            "tags": tags,
            "tags_set": tags_set,
            "difficulty": parse_difficulty(cfg),
            "timeout": parse_timeout_minutes(cfg),
            "status": status,
        }

    return catalog


# https://fr.wikipedia.org/wiki/Indice_et_distance_de_Jaccard
# a et b sont Set[str]
def jaccard(a, b):
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def format_difficulty(value: Optional[float]) -> str:
    if value is None:
        return "-"
    value = float(value)
    return str(int(value)) if value.is_integer() else str(value)


def format_timeout(value: Optional[float]) -> str:
    if value is None:
        return "-"
    value = float(value)
    return f"{int(value)} min" if value.is_integer() else f"{value} min"


def format_status(raw_status: Optional[str]) -> str:
    if raw_status == "done":
        return "fait avec succes"
    if raw_status == "failed":
        return "fait avec echec"
    return "pas encore fait"


def recommend_exercises(reference_ex: str, base_dir = "~/.trainer", top_k = 5, exclude_done = True, require_same_or_higher_difficulty = True, min_common_tags = 1):
    catalog = get_exercise_catalog(base_dir)
    ref = catalog.get(reference_ex)

    if ref is None:
        raise ValueError(f"Exercise alias introuvable: {reference_ex}")

    ref_tags = ref["tags_set"]
    ref_difficulty = ref["difficulty"]

    results: List[Dict[str, Any]] = []

    for alias, exo in catalog.items():
        if alias == reference_ex:
            continue

        if exclude_done and exo.get("status") == "done":
            continue

        exo_difficulty = exo.get("difficulty")
        if (
            require_same_or_higher_difficulty
            and ref_difficulty is not None
            and exo_difficulty is not None
            and exo_difficulty < ref_difficulty
        ):
            continue

        common_tags = ref_tags & exo["tags_set"]
        common_count = len(common_tags)

        if common_count < min_common_tags:
            continue

        results.append(
            {
                **exo,
                "common_tags": sorted(common_tags),
                "common_count": common_count,
                "jaccard": jaccard(ref_tags, exo["tags_set"]),
            }
        )
        # dans cette algo la priorite est la suivant
        # on priorise les exercices apres grand nombre tag commun apres la similarite apres difficulte apres ordre alphabetique
    results.sort(
        key=lambda e: (
            -e["common_count"],
            -e["jaccard"],
            e["difficulty"] if e["difficulty"] is not None else -1,
            e["alias"],
        )
    )

    return results[:top_k]


def print_recommendations(reference_ex, recs):
    print()
    print(f"{BOLD}{CYAN}Recommandations basees sur :{RESET} {reference_ex}")
    print(f"{DIM}{'-' * 64}{RESET}")

    if not recs:
        print("Aucune recommandation trouvee.")
        print()
        return

    for i, r in enumerate(recs, start=1):
        diff = format_difficulty(r.get("difficulty"))
        temps = format_timeout(r.get("timeout"))
        tags_communs = ", ".join(r["common_tags"]) if r["common_tags"] else "-"
        status_label = format_status(r.get("status"))
        desc = r["description"] or "-"

        if r.get("status") == "done":
            status_text = f"{GREEN}{status_label}{RESET}"
        elif r.get("status") == "failed":
            status_text = f"{RED}{status_label}{RESET}"
        else:
            status_text = status_label

        print(f"{BOLD}{i}. {r['alias']}{RESET}")
        print(f"   difficulte  : {diff}")
        print(f"   tags communs: {tags_communs}")
        print(f"   temps       : {temps}")
        print(f"   status      : {status_text}")
        print(f"   description : {desc}")
        print(f"{DIM}{'-' * 64}{RESET}")
        

def recommendRun(args) -> bool:
    try:
        recs = recommend_exercises(
            reference_ex=args.reference_alias,
            base_dir=args.base_dir,
            top_k=args.top_k,
            exclude_done=not args.include_done,
            require_same_or_higher_difficulty=not args.allow_lower_difficulty,
            min_common_tags=args.min_common_tags,
        )
        print_recommendations(args.reference_alias, recs)
        return True
    except ValueError as e:
        print(f"Erreur: {e}")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False

