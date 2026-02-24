
from arg import argParser
from importBase import importRun
from ls import lsRun
from install import installExercice

import os
import yaml
import tempfile
import shutil



def main():
    # recuperer argument
    args = argParser.parse_args()

    if args.cmd == "import":
        importRun(args)
    elif args.cmd == "ls":
        lsRun(args)
    elif args.cmd == "install":
        installExercice(args.exs, base_dir=args.base_dir, user_dir=args.user_dir)
    else:
        argParser.print_help()

if __name__ == "__main__":
    main()


