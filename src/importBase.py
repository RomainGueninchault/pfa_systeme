import argparse
import subprocess
import shutil
import sys

from pathlib import Path

def importRun(args):
    if shutil.which("git") is None:
        print("git doesn't exist")
        sys.exit(1)
    base_dir = Path(args.base_dir).expanduser()
    base_dir.mkdir(exist_ok=True)
    name = args.url.split("/")[-1].replace(".git", "")
    dest = base_dir / name
    if dest.exists():
        print("Already installed")
        # on cherche git pull apres (update par default?)
        return
    subprocess.run(["git", "clone", args.url, dest])
    print("Repository installed successfully")
    
