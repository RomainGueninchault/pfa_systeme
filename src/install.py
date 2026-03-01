import os
import yaml
import tempfile
import shutil

def installExercice(exercice_name, base_dir=None, user_dir=None):
    # Vérification que le dossier utilisateur (ou courant) est vide
    target_dir = user_dir if user_dir else os.getcwd()
    if os.path.exists(target_dir) and os.listdir(target_dir):
        print(f"Le dossier cible '{target_dir}' n'est pas vide. Installation annulée.")
        return
    """
    Copie un exercice et le dossier commun dans un dossier temporaire, compile, nettoie et copie les fichiers finaux vers le dossier utilisateur.
    """
    import subprocess
    # Détermination du répertoire de base
    home = os.path.expanduser(base_dir or "~/.base")
    if not os.path.isdir(home):
        raise RuntimeError(f"Le répertoire de base {home} n'existe pas.")

    # Recherche de l'exercice
    exo_path = None
    common_path = None
    config = None
    for repo in os.listdir(home):
        repo_path = os.path.join(home, repo)
        if not os.path.isdir(repo_path):
            continue
        for root, dirs, files in os.walk(repo_path):
            if 'config.yml' in files:
                with open(os.path.join(root, 'config.yml')) as f:
                    config = yaml.safe_load(f)
                if config.get('name') == exercice_name:
                    exo_path = root
                    # Cherche le dossier commun à la racine du dépôt
                    common_candidate = os.path.join(repo_path, 'common')
                    if os.path.isdir(common_candidate):
                        common_path = common_candidate
                    break
        if exo_path:
            break
    if not exo_path:
        print(f"Exercice '{exercice_name}' non trouvé dans {home}.")
        return False

    # Création du dossier temporaire
    tmp_dir = tempfile.mkdtemp(prefix='trainer_')
    exo_tmp = os.path.join(tmp_dir, os.path.basename(exo_path))
    shutil.copytree(exo_path, exo_tmp)
    if common_path:
        shutil.copytree(common_path, exo_tmp, dirs_exist_ok=True)
    print(f"Exercice et commun copiés dans {exo_tmp}")

    # Compilation/Préparation (commande 'prepare' dans config.yml)
    prepare_cmd = None
    if config and 'commands' in config and 'prepare' in config['commands']:
        prepare_cmd = config['commands']['prepare']
    if prepare_cmd:
        print(f"Préparation/Compilation avec : {prepare_cmd}")
        try:
            subprocess.run(prepare_cmd, shell=True, check=True, cwd=exo_tmp)
        except subprocess.CalledProcessError:
            print(f"La commande de préparation a échoué : {prepare_cmd}")
            shutil.rmtree(tmp_dir)
            return False

    # Copie uniquement les fichiers/dossiers listés dans 'distribute' du config.yml vers le dossier utilisateur
    if user_dir and config:
        distribute_files = []
        if 'distribute' in config:
            distribute_files = config['distribute']
            if isinstance(distribute_files, str):
                distribute_files = [distribute_files]
        # Toujours ajouter config.yml à la liste à copier
        if 'config.yml' not in distribute_files:
            distribute_files.append('config.yml')
        for rel_path in distribute_files:
            src_path = os.path.join(exo_tmp, rel_path)
            # Préserver la structure relative du chemin
            dest_path = os.path.join(user_dir, rel_path)
            if os.path.exists(src_path):
                if os.path.isdir(src_path):
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                else:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
        print(f"Exercice prêt dans {user_dir}")

    # Nettoyage du dossier temporaire
    shutil.rmtree(tmp_dir)
    print("Dossier temporaire supprimé.")
    return True