import os
import time
import yaml
import tempfile
import shutil
import subprocess

from install import installExercice

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
        return int(float(t) * 60)  # timeout en minutes -> secondes
    except Exception:
        return None

def ExecRun(args):
    # dossier de travail temporaire
    work_dir = tempfile.mkdtemp(prefix="trainer_work_")

    # installation dedans (ton installExercice ne change pas)
    ok = installExercice(args.exs, base_dir=args.base_dir, user_dir=work_dir)
    if not ok:
        shutil.rmtree(work_dir, ignore_errors=True)
        return False

    # timer
    start = int(time.time())
    with open(os.path.join(work_dir, ".timer_start"), "w", encoding="utf-8") as f:
        f.write(str(start))

    timeout = _timeout_seconds(work_dir)  # None si pas défini

    # rcfile bash
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

# message quand le temps est fini (sans quitter)
if [ -n "$TRAINER_TIMEOUT" ]; then
  now=$(date +%s)
  rem=$((TRAINER_TIMEOUT-(now-TRAINER_START)))
  if [ "$rem" -gt 0 ]; then
    ( sleep "$rem"; echo; echo "[trainer] Time is up." ) &
  else
    echo "[trainer] Time is up."
  fi
fi

cd "$TRAINER_WORKDIR"
''')

    # ouvrir un shell dans le dossier de travail
    subprocess.run(["bash", "--noprofile", "--rcfile", rc, "-i"], cwd=work_dir)

    # cleanup après exit
    shutil.rmtree(work_dir, ignore_errors=True)
    return True
