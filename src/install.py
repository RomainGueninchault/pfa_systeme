import os
import yaml
import tempfile
import shutil

BD = ".trainer_index.yml"

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"

def installExercice(exercice_name, base_dir=None, user_dir=None):
    # Vérification que le dossier utilisateur (ou courant) est vide
    target_dir = user_dir if user_dir else os.getcwd()
    if os.path.exists(target_dir) and os.listdir(target_dir):
        print(f"Le dossier cible '{target_dir}' n'est pas vide. Installation annulée.")
        return False
    """
    Copie un exercice et le dossier commun dans un dossier temporaire, compile, nettoie et copie les fichiers finaux vers le dossier utilisateur.
    """
    import subprocess
    # Détermination du répertoire de base
    home = os.path.expanduser(base_dir or "~/.local/share/base")
    if not os.path.isdir(home):
        raise RuntimeError(f"{RED}No DB, you must at least execute trainer import <url> once.{RESET}")

    # Recherche de l'exercice (via index YAML)
    index_path = os.path.join(home, BD)
    if not os.path.isfile(index_path):
        print(f"{RED}DB index erreur, please run trainer update to solve it.{RESET}")
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        idx = yaml.safe_load(f) or {}

    exercises = idx.get("exercises", {})
    exo_path = exercises.get(exercice_name)
    if not exo_path:
        print(f"{RED}unfound exercice '{exercice_name}'{RESET}")
        return False

    # trouver le repo racine pour common/
    rel = os.path.relpath(exo_path, home)
    repo = rel.split(os.sep, 1)[0]
    repo_path = os.path.join(home, repo)

    # common section
    common_path = None
    common_candidate = os.path.join(repo_path, "common")
    if os.path.isdir(common_candidate):
        common_path = common_candidate

    # lire config.yml de l'exercice (toujours)
    config_path = os.path.join(exo_path, "config.yml")
    if not os.path.isfile(config_path):
        print(f"No config in the exercice: {exercice_name}, please contact the owner")
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Création du dossier temporaire
    tmp_dir = tempfile.mkdtemp(prefix='trainer_')
    exo_tmp = os.path.join(tmp_dir, os.path.basename(exo_path))
    shutil.copytree(exo_path, exo_tmp)
    if common_path:
        shutil.copytree(common_path, exo_tmp, dirs_exist_ok=True)
    # print(f"Exercice et commun copiés dans {exo_tmp}")

    # Compilation/Préparation (commande 'prepare' dans config.yml)
    prepare_cmd = None
    if config and 'commands' in config and 'prepare' in config['commands']:
        prepare_cmd = config['commands']['prepare']
    if prepare_cmd:
        # print(f"Préparation/Compilation avec : {prepare_cmd}")
        try:
            subprocess.run(prepare_cmd, shell=True, check=True, cwd=exo_tmp)
        except subprocess.CalledProcessError:
            print(f"{RED}command {prepare_cmd} failed{RESET}")
            shutil.rmtree(tmp_dir)
            return False

    # Copie uniquement les fichiers/dossiers listés dans 'distribute'/'distributes' du config.yml vers le dossier cible
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
        if 'config.yml' not in distribute_files:
            distribute_files.append('config.yml')
        for rel_path in distribute_files:
            src_path = os.path.join(exo_tmp, rel_path)
            dest_path = os.path.join(target_dir, rel_path)
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                else:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
        print(f"{BLUE}Exercice is ready on {RESET}{target_dir}")

    # Nettoyage du dossier temporaire
    shutil.rmtree(tmp_dir)
    # print("Dossier temporaire supprimé.")
    return True
