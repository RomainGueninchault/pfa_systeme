import os
import yaml
import subprocess

def validateExercice(user_dir):
    """
    Exécute la commande 'validate' définie dans le config.yml de l'exercice situé dans user_dir.
    """
    config_path = os.path.join(user_dir, 'config.yml')
    if not os.path.isfile(config_path):
        print(f"config.yml introuvable dans {user_dir}.")
        return False

    with open(config_path) as f:
        config = yaml.safe_load(f)

    validate_cmd = None
    if config and 'commands' in config and 'validate' in config['commands']:
        validate_cmd = config['commands']['validate']
    else:
        print("Aucune commande 'validate' trouvée dans config.yml.")
        return False

    print(f"Validation avec : {validate_cmd}")
    try:
        subprocess.run(validate_cmd, shell=True, check=True, cwd=user_dir)
        print("Validation réussie.")
        return True
    except subprocess.CalledProcessError:
        print(f"La commande de validation a échoué : {validate_cmd}")
        return False
