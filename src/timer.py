"""Exercise timer module.

Manages exercise timing, including elapsed time tracking and timeout
notifications based on exercise configuration.
"""
import os
import time
import yaml

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"


def format_duration(seconds):
    """Format duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds.
        
    Returns:
        str: Formatted duration as 'M min S sec'.
    """
    total_seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes} min {secs} sec"


def get_elapsed_time(user_dir=None):
    """Get elapsed time since timer start.
    
    Args:
        user_dir: Directory containing the timer file (default: current directory).
        
    Returns:
        float or None: Elapsed time in seconds, or None if timer not found.
    """
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
    """Start a timer for exercise tracking.
    
    Args:
        user_dir: Directory to store timer file (default: current directory).
    """
    timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
    try:
        with open(timer_file, "w") as f:
            f.write(str(time.time()))
        print(f"{BLUE}Timer started{RESET}")
    except Exception as e:
        print(f"{RED}Error starting timer: {e}{RESET}")


def check_timer_and_report(user_dir=None, validation_result=None):
    """Check timer status and report elapsed/remaining time.
    
    Args:
        user_dir: Directory containing the timer file (default: current directory).
        validation_result: Boolean indicating if validation passed.
    """
    elapsed = get_elapsed_time(user_dir)

    if validation_result and elapsed is not None:
        print(f"{BLUE}Elapsed time : {format_duration(elapsed)}{RESET}")
        timer_file = os.path.join(user_dir if user_dir else os.getcwd(), ".timer_start")
        try:
            os.remove(timer_file)
        except Exception:
            print(f"{RED}Error removing timer{RESET}")

    elif not validation_result:
        config_path = os.path.join(user_dir if user_dir else os.getcwd(), 'config.yml')
        timeout_min = None

        if os.path.isfile(config_path):
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    timeout_min = config.get('timeout')
            except Exception:
                print(f"{RED}Error reading config.yml{RESET}")

        if elapsed is not None and timeout_min:
            print(f"{BLUE}Elapsed time : {format_duration(elapsed)}{RESET}")

            remaining_seconds = float(timeout_min) * 60.0 - elapsed

            if remaining_seconds > 0:
                print(f"{BLUE}Remaining time : {format_duration(remaining_seconds)}{RESET}")
            else:
                print(f"{RED}Time exceeded by {format_duration(abs(remaining_seconds))}{RESET}")

        elif elapsed is None:
            print(f"{RED}No timer found{RESET}")