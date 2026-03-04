from ls import rebuild_index
import subprocess
import shutil
import sys
from pathlib import Path

def importRun(args):
    if shutil.which("git") is None:
        print("git doesn't exist")
        sys.exit(1)

    base_dir = Path(args.base_dir).expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    name = args.url.split("/")[-1].removesuffix(".git")
    dest = base_dir / name

    if dest.exists():
        print("Already installed")
        return

    try:
        subprocess.run(["git", "clone", args.url, str(dest)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Clone failed (code={e.returncode})")

    # for bd    
    rebuild_index(args.base_dir)
    print("Repository installed successfully")
