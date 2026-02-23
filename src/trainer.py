
from arg import argParser
from importBase import importRun
<<<<<<< HEAD
from ls import lsRun

def main():
=======
import os
import yaml
import tempfile
import shutil





def install_exercice(exercice_name, base_dir=None, user_dir=None):
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
        return

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
            return

    # Nettoyage : suppression des fichiers non nécessaires (optionnel, à adapter)
    # Exemple : supprimer les fichiers *.tmp, *.bak, etc.
    for root, dirs, files in os.walk(exo_tmp):
        for file in files:
            if file.endswith('.tmp') or file.endswith('.bak'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    pass

    # Copie finale vers le dossier utilisateur
    if user_dir:
        for item in os.listdir(exo_tmp):
            s = os.path.join(exo_tmp, item)
            d = os.path.join(user_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print(f"Exercice prêt dans {user_dir}")

    # Nettoyage du dossier temporaire
    shutil.rmtree(tmp_dir)
    print("Dossier temporaire supprimé.")
    return True

def main():
    # recuperer argument
>>>>>>> e82158b (feat: intégration du workflow tm.py dans trainer.py)
    args = argParser.parse_args()

    if args.cmd == "import":
        importRun(args)
<<<<<<< HEAD
    elif args.cmd == "ls":
        lsRun(args)
    elif args.cmd == "install":
        print("install command:", args.exs)
=======
    elif args.cmd == "install":
        user_dir = os.getcwd()
        install_exercice(args.exs, base_dir=args.base_dir, user_dir=user_dir)
>>>>>>> e82158b (feat: intégration du workflow tm.py dans trainer.py)
    else:
        argParser.print_help()

if __name__ == "__main__":
    main()


