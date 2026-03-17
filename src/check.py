import os
import yaml
import subprocess
from history import record_done, record_failed
from timer import get_elapsed_time, format_duration
from exec import _timeout_seconds

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"

INDEX = ".trainer_index.yml"


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


def validateExercice(user_dir=None, base_dir=None):
    if not user_dir:
        user_dir = os.getcwd()
    if not base_dir:
        base_dir = "~/.local/share/base"

    config_path = os.path.join(user_dir, 'config.yml')
    if not os.path.isfile(config_path):
        print(f"{RED}config.yml introuvable dans {user_dir}{RESET}")
        return False

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception:
        print(f"{RED}Erreur lecture config.yml{RESET}")
        return False

    exo_alias = os.environ.get("TRAINER_ALIAS")
    exo_path = None

    if exo_alias:
        idx = read_index(base_dir)
        exercises = (idx.get("exercises") if isinstance(idx, dict) else {}) or {}
        exo_path = exercises.get(exo_alias)

    if not exo_path:
        print(f"{RED}Impossible de déterminer le chemin source{RESET}")
        return False

    validate_cmd = None
    if config and 'commands' in config and 'validate' in config['commands']:
        validate_cmd = config['commands']['validate']
    else:
        print(f"{RED}Commande 'validate' absente dans config.yml{RESET}")
        return False

    print(f"{BLUE}Validation avec : {validate_cmd}{RESET}")

    try:
        subprocess.run(validate_cmd, shell=True, check=True, cwd=user_dir)
        print(f"{BLUE}Validation réussie{RESET}")

        elapsed = get_elapsed_time(user_dir)
        time_str = None

        if elapsed is not None:
            timeout_seconds = _timeout_seconds(user_dir)
            if timeout_seconds is not None and elapsed > timeout_seconds:
                time_str = "overtime"
            else:
                time_str = format_duration(elapsed)

        record_done(exo_path, time_str=time_str)
        return True

    except subprocess.CalledProcessError:
        print(f"{RED}Validation échouée : {validate_cmd}{RESET}")
        record_failed(exo_path)
        return False