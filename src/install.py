"""Exercise installation module.

Handles installation of exercises by copying files, merging configurations,
and preparing exercise environments for users.
"""
import os
import yaml
import tempfile
import shutil
from ls import load_merged_config

BD = ".trainer_index.yml"

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"

def installExercice(exercice_name, base_dir=None, user_dir=None):
    """Install an exercise to a user directory.
    
    Copies exercise files, merges configurations from repository and exercise
    directories, runs preparation commands, and distributes specified files
    to the target directory.
    
    Args:
        exercice_name: Name/alias of the exercise to install.
        base_dir: Base directory for exercises (default: ~/.trainer).
        user_dir: Target directory for installation (default: current directory).
        
    Returns:
        bool: True if installation succeeded, False otherwise.
    """
    target_dir = user_dir if user_dir else os.getcwd()
    if os.path.exists(target_dir) and os.listdir(target_dir):
        print(f"Target directory '{target_dir}' is not empty. Installation canceled.")
        return False
    """
    Copy an exercise and the common directory to a temporary directory, compile, clean and copy the final files to the user directory.
    """
    import subprocess
    # Determine the base directory
    home = os.path.expanduser(base_dir or "~/.trainer")
    if not os.path.isdir(home):
        raise RuntimeError(f"{RED}No DB, you must at least execute trainer import <url> once.{RESET}")

    # Search for the exercise (via YAML index)
    index_path = os.path.join(home, BD)
    if not os.path.isfile(index_path):
        print(f"{RED}DB index error, please run trainer update to solve it.{RESET}")
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        idx = yaml.safe_load(f) or {}

    exercises = idx.get("exercises", {})
    exo_path = exercises.get(exercice_name)
    if not exo_path:
        print(f"{RED}exercise '{exercice_name}' not found{RESET}")
        return False

    # Find the root repo for common/
    rel = os.path.relpath(exo_path, home)
    repo = rel.split(os.sep, 1)[0]
    repo_path = os.path.join(home, repo)

    # common section
    common_path = None
    common_candidate = os.path.join(repo_path, "common")
    if os.path.isdir(common_candidate):
        common_path = common_candidate

    # Read merged config.yml (repo + exercise)
    config = load_merged_config(exo_path, home)
    if not config:
        print(f"No config found for exercise: {exercice_name}, please contact the owner")
        return False

    # Create temporary directory
    tmp_dir = tempfile.mkdtemp(prefix='trainer_')
    exo_tmp = os.path.join(tmp_dir, os.path.basename(exo_path))
    shutil.copytree(exo_path, exo_tmp)
    if common_path:
        shutil.copytree(common_path, exo_tmp, dirs_exist_ok=True)

    # Write merged config to temporary directory (to have validate from repo if needed)
    merged_config_path = os.path.join(exo_tmp, "config.yml")
    with open(merged_config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    # print(f"Exercise and common copied to {exo_tmp}")

    # Compilation/Preparation (command 'prepare' in config.yml)
    prepare_cmd = None
    if config and 'commands' in config and 'prepare' in config['commands']:
        prepare_cmd = config['commands']['prepare']
    if prepare_cmd:
        # print(f"Preparation/Compilation with: {prepare_cmd}")
        try:
            subprocess.run(prepare_cmd, shell=True, check=True, cwd=exo_tmp)
        except subprocess.CalledProcessError:
            print(f"{RED}command {prepare_cmd} failed{RESET}")
            shutil.rmtree(tmp_dir)
            return False

    # Only copy files/folders listed in 'distribute'/'distributes' from config.yml to target directory
    distributed_sources = set()  # Track source files that have been distributed
    if config:
        distribute_files = []
        if 'distribute' in config:
            distribute_files = config['distribute']
            if isinstance(distribute_files, str):
                distribute_files = [distribute_files]
        elif 'distributes' in config:
            distribute_files = config['distributes']
            if isinstance(distribute_files, str):
                distribute_files = [distribute_files]

        # Add config.yml if not already in the list
        if not isinstance(distribute_files, list):
            distribute_files = []

        # Check if config.yml is in the list (as string, not as dict)
        has_config_yml = any(\
            (isinstance(item, str) and item == 'config.yml') or \
            (isinstance(item, dict) and 'config.yml' in item) \
            for item in distribute_files\
        )
        if not has_config_yml:
            distribute_files.append('config.yml')

        if distribute_files:
            for item in distribute_files:
                # Handle both strings and mappings (source: destination)
                if isinstance(item, dict):
                    # Format: {source: destination}
                    for src_rel, dest_rel in item.items():
                        src_path = os.path.join(exo_tmp, src_rel)
                        dest_path = os.path.join(target_dir, dest_rel)
                        distributed_sources.add(src_rel)  # Track source file
                        if os.path.exists(src_path):
                            if os.path.isdir(src_path):
                                if os.path.exists(dest_path):
                                    shutil.rmtree(dest_path)
                                shutil.copytree(src_path, dest_path)
                            else:
                                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                shutil.copy2(src_path, dest_path)
                else:
                    # Format: simple string
                    rel_path = str(item)
                    src_path = os.path.join(exo_tmp, rel_path)
                    dest_path = os.path.join(target_dir, rel_path)
                    distributed_sources.add(rel_path)  # Track source file
                    if os.path.exists(src_path):
                        if os.path.isdir(src_path):
                            if os.path.exists(dest_path):
                                shutil.rmtree(dest_path)
                            shutil.copytree(src_path, dest_path)
                        else:
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(src_path, dest_path)
            print(f"{BLUE}Exercise is ready on {RESET}{target_dir}")

    # Also copy common files that have not already been distributed
    if common_path and os.path.isdir(common_path):
        for item in os.listdir(common_path):
            # Do not copy files that have been listed as source in distribute
            if item in distributed_sources:
                continue

            src_item = os.path.join(common_path, item)
            dest_item = os.path.join(target_dir, item)
            # Do not overwrite files already distributed or created
            if not os.path.exists(dest_item):
                if os.path.isdir(src_item):
                    shutil.copytree(src_item, dest_item)
                else:
                    shutil.copy2(src_item, dest_item)

    # Clean up temporary directory
    shutil.rmtree(tmp_dir)
    # print("Temporary directory deleted.")
    return True
