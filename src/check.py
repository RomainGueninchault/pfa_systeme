"""Exercise validation module for the trainer application.

Handles validation of exercise solutions by running test commands and recording
results in the history file.
"""
import os
import shutil
import yaml
import subprocess
from history import record_done, record_failed
from timer import get_elapsed_time, format_duration
from execRun import _timeout_seconds

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"

INDEX = ".trainer_index.yml"


def read_index(base_dir):
    """Read the exercise index from the base directory.
    
    Args:
        base_dir: The base directory containing the index file.
        
    Returns:
        dict: The index data, or empty dict if not found or on error.
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


def validateExercice(user_dir=None, base_dir=None):
    """Validate an exercise solution by running test commands.
    
    Args:
        user_dir: Directory containing the exercise solution.
        base_dir: Base directory for exercises.
        
    Returns:
        bool: True if validation passed, False otherwise.
    """
    if not user_dir:
        user_dir = os.getcwd()
    if not base_dir:
        base_dir = "~/.trainer"

    config_path = os.path.join(user_dir, 'config.yml')
    if not os.path.isfile(config_path):
        print(f"{RED}config.yml not found in {user_dir}{RESET}")
        return False

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception:
        print(f"{RED}Error reading config.yml{RESET}")
        return False

    exo_alias = os.environ.get("TRAINER_ALIAS")

    if not exo_alias:
        print(f"{RED}Variable TRAINER_ALIAS not set{RESET}")
        return False
    
    if config and config.get('language') == "javascript":
        index = read_index(base_dir)
        
        exercises = index.get("exercises", {})
        
        if exo_alias not in exercises:
            print(f"{RED}Unknown alias in index{RESET}")
            return False
        
        real_base = exercises[exo_alias]

        test_files = config.get("test", [])
        if not isinstance(test_files, list):
            print(f"{RED}Field 'test' must be a list{RESET}")
            return False

        for file in test_files:
            src = os.path.join(real_base, file)
            dst = os.path.join(user_dir, file)

            if not os.path.isfile(src):
                print(f"{YELLOW}Test file not found: {src}{RESET}")
                continue

            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)

        print(f"{BLUE}Test files copied (JS){RESET}")

    validate_cmd = None
    if config and 'commands' in config and 'validate' in config['commands']:
        validate_cmd = config['commands']['validate']
    else:
        print(f"{RED}Command 'validate' missing from config.yml{RESET}")
        return False

    print(f"{BLUE}Validating with: {validate_cmd}{RESET}")

    try:
        subprocess.run(validate_cmd, shell=True, check=True, cwd=user_dir)
        print(f"{BLUE}Validation successful{RESET}")

        elapsed = get_elapsed_time(user_dir)
        time_str = None

        if elapsed is not None:
            timeout_seconds = _timeout_seconds(user_dir)
            if timeout_seconds is not None and elapsed > timeout_seconds:
                time_str = "overtime"
            else:
                time_str = format_duration(elapsed)

        record_done(exo_alias, time_str=time_str)
        return True

    except subprocess.CalledProcessError:
        print(f"{RED}Validation failed: {validate_cmd}{RESET}")
        record_failed(exo_alias)
        return False
