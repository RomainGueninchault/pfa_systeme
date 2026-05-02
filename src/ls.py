"""Exercise listing and indexing module.

Provides functionality to list exercises, rebuild the exercise index,
merge configurations from repository and exercise directories, and format
exercise information for display.
"""
import os
import yaml
import shutil
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

# for recursion
def find_cfg_in_dir(dirpath):
    """Find a configuration file in a directory.
    
    Args:
        dirpath: Directory to search for config files.
        
    Returns:
        str or None: Path to config file, or None if not found.
    """
    for fn in CFG:
        p = os.path.join(dirpath, fn)
        if os.path.isfile(p):
            return p
    return None


def merge_tags(parent_value, child_value):
    """Merge tag lists from parent and child configurations.
    
    Args:
        parent_value: Parent configuration tags.
        child_value: Child configuration tags.
        
    Returns:
        list: Merged tags with deduplication.
    """
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
    Merge parent -> child.
    - dict + dict  => recursive merge
    - tags         => concatenate + deduplication
    - otherwise    => child value overwrites parent value
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
    Climb from leaf to repository root
    and merge all YAML files found.
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
    for cfg_path in reversed(stack):   # root -> leaf
        merged = deep_merge(merged, yml(cfg_path))

    return merged


def get_exercise_status(alias):
    """Returns the exercise status: (status, time).
    
    Status can be:
    - 'not_started' : no history
    - 'started' : started but not completed/failed
    - 'failed' : attempted but failed
    - 'done_in_time' : completed within time limit
    - 'done_overtime' : completed but exceeded time limit
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
    """Returns the ANSI color for a given status."""
    color_map = {
        'not_started': CYAN,
        'started': YELLOW,
        'failed': RED,
        'done_in_time': GREEN,
        'done_overtime': ORANGE,
    }
    return color_map.get(status, CYAN)

def get_repo_name(ex_dir, base_dir):
    """Extract the repository name from the exercise path.
    
    Returns the directory name immediately after base_dir.
    Ex: ~/.trainer/mon_repo/exercise -> mon_repo
    """
    root = os.path.expanduser(base_dir)
    rel_path = os.path.relpath(ex_dir, root)
    parts = rel_path.split(os.sep)
    return parts[0] if parts else ""

def truncate_string(text, width):
    """Truncates text to a fixed width with '...' if necessary."""
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return text[:width - 3] + "..."

def wrap_description(desc, desc_w):
    """Split a description into lines of max desc_w characters."""
    desc_lines = []
    remaining = desc
    while remaining:
        if len(remaining) <= desc_w:
            desc_lines.append(remaining)
            break
        else:
            chunk = remaining[:desc_w]
            last_space = chunk.rfind(' ')
            
            if last_space > 0 and last_space > desc_w // 2:
                desc_lines.append(remaining[:last_space])
                remaining = remaining[last_space + 1:]
            else:
                desc_lines.append(chunk)
                remaining = remaining[desc_w:]
    return desc_lines

def format_row_with_wrapping(name, tags, repo, desc, name_w, tags_w, repo_w, desc_w, status, show_repo=True):
    """
    Format a complete row with column management.
    Wrap the description on multiple lines if it exceeds desc_w.
    Returns a list of lines to display.
    """
    color = get_status_color(status)
    
    # Tronquer et padder les colonnes fixes
    name_part = truncate_string(name, name_w).ljust(name_w)
    tags_part = truncate_string(tags, tags_w).ljust(tags_w)

    lines = []
    desc_lines = wrap_description(desc, desc_w)
    
    # Première ligne avec toutes les colonnes
    if desc_lines:
        if show_repo:
            repo_part = truncate_string(repo, repo_w).ljust(repo_w)
            line = color + name_part + RESET + "     " + tags_part + "     " + repo_part + "     " + desc_lines[0]
            indent = " " * (name_w + 5 + tags_w + 5 + repo_w + 5)
        else:
            line = color + name_part + RESET + "     " + tags_part + "     " + desc_lines[0]
            indent = " " * (name_w + 5 + tags_w + 5)

        lines.append(line)
        
        # Lignes suivantes pour la description (indentées)
        for desc_line in desc_lines[1:]:
            lines.append(indent + desc_line)
    else:
        # Ligne vide
        if show_repo:
            repo_part = truncate_string(repo, repo_w).ljust(repo_w)
            line = color + name_part + RESET + "     " + tags_part + "     " + repo_part
        else:
            line = color + name_part + RESET + "     " + tags_part
        lines.append(line)
    
    return lines

def yml(pathFile):
    """Load YAML file safely.
    
    Args:
        pathFile: Path to the YAML file.
        
    Returns:
        dict: Parsed YAML content, or empty dict on error.
    """
    try:
        with open(pathFile, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def leaf(dirpath):
    """Check if a directory is a leaf (contains no subdirectories).
    
    Args:
        dirpath: Directory path to check.
        
    Returns:
        bool: True if directory has no subdirectories, False otherwise.
    """
    try:
        for name in os.listdir(dirpath):
            if os.path.isdir(os.path.join(dirpath, name)):
                return False
        return True
    except Exception:
        return False

def exName(pathFile, base_dir=None):
    """Extract exercise name from configuration.
    
    Args:
        pathFile: Path to the config file.
        base_dir: Base directory for merged config (optional).
        
    Returns:
        str: Exercise name from config or directory basename.
    """
    if base_dir is not None:
        ex_dir = os.path.dirname(pathFile)
        c = load_merged_config(ex_dir, base_dir)
    else:
        c = yml(pathFile)

    n = c.get("name")
    if isinstance(n, str) and n.strip():
        return n.strip()
    return os.path.basename(os.path.dirname(pathFile))


def tags_norm(v):
    """Normalize tags from various formats.
    
    Args:
        v: Tags in various formats (list, string, comma-separated, space-separated).
        
    Returns:
        list: Normalized tag list.
    """
    if v is None: return []
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s: return []
    return [t.strip() for t in s.split(",")] if "," in s else s.split()

def rebuild_index(base_dir):
    """Rebuild the exercise index from the repository structure.
    
    Args:
        base_dir: Base directory containing exercise repositories.
    """
    root = os.path.expanduser(base_dir)
    
    found = [] 
    for repo_name in sorted(os.listdir(root)):
        repo_path = os.path.join(root, repo_name)
        if not os.path.isdir(repo_path):
            continue

        for dirpath, dirnames, filenames in os.walk(repo_path):
            # ignore config at repository root
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
    """Read the exercise index file.
    
    Args:
        base_dir: Base directory for the index.
        
    Returns:
        dict: The index data, or empty dict if not found.
    """
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

def calculate_column_widths(rows, terminal_width, show_repo=True):
    """Calculate appropriate column widths based on terminal width.
    
    Args:
        rows: List of exercise rows to display.
        terminal_width: Width of the terminal.
        show_repo: Whether to include repository name column.
        
    Returns:
        tuple: (name_width, tags_width, repo_width, description_width, total_fixed_width)
    """
    name_w = max(len(r[0]) for r in rows)
    tags_w = max(len(r[1]) for r in rows)

    name_w = max(name_w, len("NAME"))
    tags_w = max(tags_w, len("TAGS"))

    # spacing between columns
    spacing = 5  # "     "

    if show_repo:
        repo_w = max(len(r[5]) for r in rows)
        repo_w = max(repo_w, len("REPO"))
        total_fixed = name_w + tags_w + repo_w + (spacing * 3)
    else:
        repo_w = 0
        total_fixed = name_w + tags_w + (spacing * 2)

    # description takes the remaining space, at least 30 chars
    desc_w = max(30, terminal_width - total_fixed - 10)
    
    if total_fixed >= terminal_width - 30:
        name_w = max(5, int(name_w * 0.6))
        tags_w = max(5, int(tags_w * 0.6))
        if show_repo:
            repo_w = max(5, int(repo_w * 0.6))
            total_fixed = name_w + tags_w + repo_w + (spacing * 3)
        else:
            total_fixed = name_w + tags_w + (spacing * 2)
        desc_w = max(20, terminal_width - total_fixed - 5)

    return name_w, tags_w, repo_w, desc_w, total_fixed

def lsRun(args):
    """List exercises with filtering and formatting.
    
    Displays exercises from the index with support for filtering by tags,
    repository, and completion status. Formats output with proper column
    alignment and status colors.
    
    Args:
        args: Command-line arguments containing base_dir, tag, done, and repo filters.
    """
    idx = read_index(args.base_dir)
    exercises = (idx.get("exercises") if isinstance(idx, dict) else {}) or {}

    if not exercises:
        print(RED + "Index absent/vidé. Lance d'abord: trainer import <url> (qui rebuild l'index)." + RESET)
        return

    tf = (args.tag or "").strip().lower()
    show_done = getattr(args, 'done', False)
    repo_filter = (args.repo or "").strip() if hasattr(args, 'repo') else ""

    rows = []

    for alias in sorted(exercises):
        ex_dir = exercises[alias]
        cfg = os.path.join(ex_dir, "config.yml")
        if not os.path.isfile(cfg):
            cfg2 = os.path.join(ex_dir, "config.yaml")
            if not os.path.isfile(cfg2):
                continue
            cfg = cfg2

        # Appliquer le filtre par répertoire si spécifié
        if repo_filter:
            repo_name = get_repo_name(ex_dir, args.base_dir)
            if repo_name != repo_filter:
                continue

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
    
    # Déterminer si on affiche la colonne REPO
    show_repo = not repo_filter

    # Obtenir la taille du terminal et calculer les largeurs de colonnes
    terminal_width = shutil.get_terminal_size((80, 24)).columns
    name_w, tags_w, repo_w, desc_w, total_fixed = calculate_column_widths(rows, terminal_width, show_repo=show_repo)

    # Formater le header avec alignement à gauche
    if show_repo:
        header = (GREEN + "NAME".ljust(name_w) + RESET + "     " +
                  BLUE + "TAGS".ljust(tags_w) + RESET + "     " +
                  ORANGE + "REPO".ljust(repo_w) + RESET + "     " +
                  MAGENTA + "DESCRIPTION" + RESET)
    else:
        header = (GREEN + "NAME".ljust(name_w) + RESET + "     " +
                  BLUE + "TAGS".ljust(tags_w) + RESET + "     " +
                  MAGENTA + "DESCRIPTION" + RESET)

    print(header)
    print("-" * min(terminal_width - 1, total_fixed + desc_w))

    for name, tags, desc, status, time_info, repo in rows:
        for line in format_row_with_wrapping(name, tags, repo, desc, name_w, tags_w, repo_w, desc_w, status, show_repo=show_repo):
            print(line)
