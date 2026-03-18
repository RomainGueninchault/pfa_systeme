import os
import yaml
from history import exo_hash, HISTORY_FILE

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
CYAN    = "\033[36m"
BOLD    = "\033[1m"


def yml(pathFile):
    try:
        with open(pathFile, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def show_stats(args):
    base_dir = os.path.expanduser("~/.trainer/pfa_exercices")
    hist = yml(HISTORY_FILE)

    print(f"{BOLD}{CYAN}=== STATISTICS ==={RESET}\n")

    for name in sorted(os.listdir(base_dir)):
        path = os.path.join(base_dir, name)

        if not os.path.isdir(path):
            continue

        h = exo_hash(path)
        entry = hist.get(h)

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

        # Affichage
        line = f"{BOLD}{name:<25}{RESET} | {status_str}"

        if status == "done" and time:
            line += f" | {BLUE}time:{RESET} {time}"

        print(line)

    print()
