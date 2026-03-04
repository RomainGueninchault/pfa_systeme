import os
import time
import yaml


def format_duration(seconds):
    total_seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes} min {secs} sec"

def start_timer(user_dir=None):
    timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
    with open(timer_file, "w") as f:
        f.write(str(time.time()))
    print("Timer démarré. Lancez 'check' avec une validation réussie pour arrêter le timer.")

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
        print(f"Temps écoulé pour compléter l'exercice : {format_duration(elapsed)}.")
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
            elapsed_seconds = time.time() - start_time
            print(f"Temps écoulé depuis le début de l'exercice : {format_duration(elapsed_seconds)}.")
            remaining_seconds = float(timeout_min) * 60.0 - elapsed_seconds
            if remaining_seconds > 0:
                print(f"Temps restant avant timeout : {format_duration(remaining_seconds)}.")
            else:
                print(f"Temps imparti dépassé de {format_duration(abs(remaining_seconds))} !")
    elif not start_time:
        print("Aucun timer trouvé.")

