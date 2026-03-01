
import os
import time
import yaml

def start_timer(user_dir=None):
    timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
    with open(timer_file, "w") as f:
        f.write(str(time.time()))
    print("Timer démarré. Lancez 'check' pour arrêter le timer.")

def check_timer_and_report(user_dir=None, validation_result=None):
    timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
    start_time = None
    if os.path.exists(timer_file):
        with open(timer_file, "r") as f:
            try:
                start_time = float(f.read().strip())
            except Exception:
                start_time = None
    if validation_result and start_time:
        elapsed = time.time() - start_time
        print(f"Temps écoulé pour compléter l'exercice : {elapsed:.1f} secondes.")
        os.remove(timer_file)
    elif not validation_result:
        # Affiche le temps restant avant le timeout si défini
        config_path = os.path.join(user_dir if user_dir else os.getcwd(), 'config.yml')
        timeout_min = None
        if os.path.isfile(config_path):
            with open(config_path) as f:
                try:
                    config = yaml.safe_load(f)
                    timeout_min = config.get('timeout')
                except Exception:
                    timeout_min = None
        if start_time and timeout_min:
            elapsed = (time.time() - start_time) / 60.0
            remaining = float(timeout_min) - elapsed
            if remaining > 0:
                print(f"Temps restant avant timeout : {remaining:.1f} minutes.")
            else:
                print("Temps imparti dépassé !")
        else:
            print("L'exercice n'est pas encore correct, timer conservé.")
    elif not start_time:
        print("Aucun timer trouvé.")

