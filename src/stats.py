"""Exercise statistics display module.

Displays statistics about completed, failed, and attempted exercises from
the history file with colored output.
"""
import os
import yaml
from history import HISTORY_FILE
from ls import read_index

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
CYAN    = "\033[36m"
BOLD    = "\033[1m"


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


def show_stats(args):
    """Display exercise completion statistics.
    
    Shows completed, failed, and attempted exercises from the history file
    with colored status indicators and completion times.
    
    Args:
        args: Command-line arguments containing base_dir.
    """
    base_dir = os.path.expanduser(args.base_dir if hasattr(args, 'base_dir') else "~/.trainer")
    hist = yml(HISTORY_FILE)
    idx = read_index(base_dir)
    exercises = (idx.get("exercises") if isinstance(idx, dict) else {}) or {}

    print(f"{BOLD}{CYAN}=== STATISTICS ==={RESET}\n")

    for alias in sorted(exercises):
        entry = hist.get(alias)

        if not entry:
            continue

        status = entry.get("status")
        time = entry.get("time")

        if status == "done":
            color = GREEN
            status_str = f"{GREEN}DONE{RESET}"
        elif status == "failed":
            color = RED
            status_str = f"{RED}FAILED{RESET}"
        else:
            color = YELLOW
            status_str = f"{YELLOW}{status.upper()}{RESET}"

        # Display
        line = f"{BOLD}{alias:<25}{RESET} | {status_str}"

        if status == "done" and time:
            line += f" | {BLUE}time:{RESET} {time}"

        print(line)

    print()
