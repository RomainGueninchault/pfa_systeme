import os
import time
import yaml
import tempfile
import shutil
import subprocess

from install import installExercice

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"


def _timeout_seconds(work_dir):
    pathYml = os.path.join(work_dir, "config.yml")
    if not os.path.isfile(pathYml):
        return None
    try:
        with open(pathYml, "r", encoding="utf-8") as f:
            c = yaml.safe_load(f) or {}
        t = c.get("timeout")
        if t is None:
            return None
        return int(float(t) * 60)
    except Exception:
        return None


def ExecRun(args):
    work_dir = tempfile.mkdtemp(prefix="trainer_work_")

    try:
        print(f"{BLUE}Installing exercise...{RESET}")
        ok = installExercice(args.exs, base_dir=args.base_dir, user_dir=work_dir)
        if not ok:
            print(f"{RED}Installation failed{RESET}")
            return False

        print(f"{BLUE}Installation successful{RESET}")

        start = int(time.time())
        with open(os.path.join(work_dir, ".timer_start"), "w", encoding="utf-8") as f:
            f.write(str(start))

        timeout = _timeout_seconds(work_dir)

        if timeout is not None:
            print(f"{BLUE}Timeout detected: {timeout}s{RESET}")
        else:
            print(f"{BLUE}No timeout defined{RESET}")

        rc = os.path.join(work_dir, ".trainer_rc")
        with open(rc, "w", encoding="utf-8") as f:
            f.write(f'export TRAINER_START={start}\n')
            f.write(f'export TRAINER_TIMEOUT={timeout if timeout is not None else ""}\n')
            f.write(f'export TRAINER_ALIAS="{args.exs}"\n')
            f.write(f'export TRAINER_WORKDIR="{work_dir}"\n')
            f.write(r'''
trainer_prompt() {
  if [ -n "$TRAINER_TIMEOUT" ]; then
    now=$(date +%s)
    passer=$((now-TRAINER_START))
    rem=$((TRAINER_TIMEOUT-passer))

    if [ "$rem" -gt 0 ]; then
      m=$((rem/60)); s=$((rem%60))
      PS1="(trainer:$TRAINER_ALIAS ${m}m${s}s left) \u@\h:\w\$ "
    else
      PS1="(trainer:$TRAINER_ALIAS TIME OVER) \u@\h:\w\$ "
    fi
  else
    PS1="(trainer:$TRAINER_ALIAS) \u@\h:\w\$ "
  fi
}

PROMPT_COMMAND=trainer_prompt
trainer_prompt

TRAINER_TIMER_PID=""

if [ -n "$TRAINER_TIMEOUT" ]; then
  now=$(date +%s)
  rem=$((TRAINER_TIMEOUT-(now-TRAINER_START)))
  if [ "$rem" -gt 0 ]; then
    (
      sleep "$rem"
      printf '\n[trainer] Time is up.\n'
    ) &
    TRAINER_TIMER_PID=$!
    disown "$TRAINER_TIMER_PID" 2>/dev/null || disown %% 2>/dev/null || true
  else
    echo "[trainer] Time is up."
  fi
fi

trap '
  if [ -n "${TRAINER_TIMER_PID:-}" ]; then
    kill -- -"$TRAINER_TIMER_PID" 2>/dev/null || kill "$TRAINER_TIMER_PID" 2>/dev/null || true
  fi
' EXIT HUP INT TERM

cd "$TRAINER_WORKDIR"
''')
        print(f"{BLUE}Launching sandbox shell{RESET}")
        subprocess.run(["bash", "--noprofile", "--rcfile", rc, "-i"], cwd=work_dir)

        print(f"{BLUE}Session ended{RESET}")
        return True

    except Exception as e:
        print(f"{RED}Execution error: {e}{RESET}")
        return False

    finally:
        print(f"{BLUE}Cleaning up...{RESET}")
        shutil.rmtree(work_dir, ignore_errors=True)
