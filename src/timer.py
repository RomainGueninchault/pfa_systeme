import os
import time
import yaml

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"


def format_duration(seconds):
    total_seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes} min {secs} sec"


def get_elapsed_time(user_dir=None):
    timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
    if not os.path.exists(timer_file):
        return None
    try:
        with open(timer_file, "r") as f:
            start_time = float(f.read().strip())
        return time.time() - start_time
    except Exception:
        return None


def start_timer(user_dir=None):
    timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
    try:
        with open(timer_file, "w") as f:
            f.write(str(time.time()))
        print(f"{BLUE}Timer démarré{RESET}")
    except Exception as e:
        print(f"{RED}Erreur démarrage timer: {e}{RESET}")


def check_timer_and_report(user_dir=None, validation_result=None):
    elapsed = get_elapsed_time(user_dir)

    if validation_result and elapsed is not None:
        print(f"{BLUE}Temps écoulé : {format_duration(elapsed)}{RESET}")
        timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
        try:
            os.remove(timer_file)
        except Exception:
            print(f"{RED}Erreur suppression timer{RESET}")

    elif not validation_result:
        config_path = os.path.join(user_dir if user_dir else os.getcwd(), 'config.yml')
        timeout_min = None

        if os.path.isfile(config_path):
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    timeout_min = config.get('timeout')
            except Exception:
                print(f"{RED}Erreur lecture config.yml{RESET}")

        if elapsed is not None and timeout_min:
            print(f"{BLUE}Temps écoulé : {format_duration(elapsed)}{RESET}")

            remaining_seconds = float(timeout_min) * 60.0 - elapsed

            if remaining_seconds > 0:
                print(f"{BLUE}Temps restant : {format_duration(remaining_seconds)}{RESET}")
            else:
                print(f"{RED}Temps dépassé de {format_duration(abs(remaining_seconds))}{RESET}")

        elif elapsed is None:
            print(f"{RED}Aucun timer trouvé{RESET}")