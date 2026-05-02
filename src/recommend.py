"""Exercise recommendation engine module.

Provides intelligent recommendations for exercises based on a reference
exercise using similarity metrics like Jaccard index and tag analysis.
"""
import os
import argparse
from typing import Any, Dict, List, Optional, Set

import yaml

from ls import read_index, tags_norm
from history import HISTORY_FILE

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
    """Load YAML file safely.
    
    Args:
        path: Path to the YAML file.
        
    Returns:
        dict: Parsed YAML content, or empty dict on error.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

    
def find_config(exo_dir):
    """Find configuration file in exercise directory.
    
    Args:
        exo_dir: Exercise directory to search.
        
    Returns:
        str or None: Path to config file, or None if not found.
    """
    for name in CFG_NAMES:
        path = os.path.join(exo_dir, name)
        if os.path.isfile(path):
            return path
    return None


# cfg is returned by yml on config.yml
def parse_difficulty(cfg):
    """Parse difficulty value from exercise configuration.
    
    Args:
        cfg: Exercise configuration dictionary.
        
    Returns:
        float or None: Difficulty value, or None if not set or invalid.
    """
    value = cfg.get("difficulty")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_timeout_minutes(cfg):
    """Parse timeout value in minutes from exercise configuration.
    
    Args:
        cfg: Exercise configuration dictionary.
        
    Returns:
        float or None: Timeout in minutes, or None if not set or invalid.
    """
    value = cfg.get("timeout")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

# return Dict[str, Dict[str, Any]] first str is exercise name and others are metadata
def get_exercise_catalog(base_dir: str) -> Dict[str, Dict[str, Any]]:
    """Build a catalog of all exercises with metadata.
    
    Args:
        base_dir: Base directory containing exercises.
        
    Returns:
        dict: Catalog mapping exercise aliases to their metadata.
    """
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

        history_entry = history.get(alias, {})
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


# https://en.wikipedia.org/wiki/Jaccard_index
# a and b are Set[str]
def jaccard(a, b):
    """Calculate Jaccard similarity between two sets.
    
    Args:
        a: First set.
        b: Second set.
        
    Returns:
        float: Jaccard similarity score between 0 and 1.
    """
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def format_difficulty(value: Optional[float]) -> str:
    """Format difficulty value for display.
    
    Args:
        value: Difficulty value.
        
    Returns:
        str: Formatted difficulty string.
    """
    if value is None:
        return "-"
    value = float(value)
    return str(int(value)) if value.is_integer() else str(value)


def format_timeout(value: Optional[float]) -> str:
    """Format timeout value for display.
    
    Args:
        value: Timeout in minutes.
        
    Returns:
        str: Formatted timeout string.
    """
    if value is None:
        return "-"
    value = float(value)
    return f"{int(value)} min" if value.is_integer() else f"{value} min"


def format_status(raw_status: Optional[str]) -> str:
    """Format exercise status for display.
    
    Args:
        raw_status: Raw status string from history.
        
    Returns:
        str: Human-readable status string.
    """
    if raw_status == "done":
        return "completed successfully"
    if raw_status == "failed":
        return "completed with failure"
    return "not yet completed"


def recommend_exercises(reference_ex: str, base_dir = "~/.trainer", top_k = 5, exclude_done = True, require_same_or_higher_difficulty = True, min_common_tags = 1):
    """Recommend exercises similar to a reference exercise.
    
    Args:
        reference_ex: Alias of the reference exercise.
        base_dir: Base directory for exercises.
        top_k: Maximum number of recommendations.
        exclude_done: Whether to exclude completed exercises.
        require_same_or_higher_difficulty: Filter by difficulty.
        min_common_tags: Minimum common tags required.
        
    Returns:
        list: Recommended exercises sorted by relevance.
    """
    catalog = get_exercise_catalog(base_dir)
    ref = catalog.get(reference_ex)

    if ref is None:
        raise ValueError(f"Exercise alias not found: {reference_ex}")

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
        # In this algorithm the priority is as follows:
        # prioritize exercises by number of common tags, then by similarity, then by difficulty, then alphabetically
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
    """Display exercise recommendations in formatted output.
    
    Args:
        reference_ex: Alias of the reference exercise.
        recs: List of recommended exercises.
    """
    print()
    print(f"{BOLD}{CYAN}Recommendations based on:{RESET} {reference_ex}")
    print(f"{DIM}{'-' * 64}{RESET}")

    if not recs:
        print("No recommendations found.")
        print()
        return

    for i, r in enumerate(recs, start=1):
        diff = format_difficulty(r.get("difficulty"))
        time = format_timeout(r.get("timeout"))
        common_tags = ", ".join(r["common_tags"]) if r["common_tags"] else "-"
        status_label = format_status(r.get("status"))
        desc = r["description"] or "-"

        if r.get("status") == "done":
            status_text = f"{GREEN}{status_label}{RESET}"
        elif r.get("status") == "failed":
            status_text = f"{RED}{status_label}{RESET}"
        else:
            status_text = status_label

        print(f"{BOLD}{i}. {r['alias']}{RESET}")
        print(f"   difficulty  : {diff}")
        print(f"   common tags : {common_tags}")
        print(f"   time        : {time}")
        print(f"   status      : {status_text}")
        print(f"   description : {desc}")
        print(f"{DIM}{'-' * 64}{RESET}")
        

def recommendRun(args) -> bool:
    """Process recommendation command-line request.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        bool: True if successful, False on error.
    """
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
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

