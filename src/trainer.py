"""Main entry point for the trainer application.

Orchestrates all subcommands and directs user input to appropriate
modules for exercise management.
"""
from execRun import ExecRun
from arg import argParser
from importBase import importRun, pullRun
from ls import lsRun
from install import installExercice
from check import validateExercice
from timer import start_timer, check_timer_and_report
from stats import show_stats
from recommend import recommendRun

import os
import yaml
import tempfile
import shutil


def main():
    """Main entry point for the trainer application.
    
    Parses command-line arguments and dispatches to the appropriate
    command handler (import, list, install, check, exec, update, stats, recommend).
    """
    args = argParser.parse_args()

    if args.cmd == "import":
        importRun(args)
    elif args.cmd == "ls":
        lsRun(args)
    elif args.cmd == "install":
        result_install = installExercice(args.exs, base_dir=args.base_dir, user_dir=args.user_dir)
    elif args.cmd == "check":
        result=validateExercice(user_dir=args.user_dir, base_dir=args.base_dir)
        check_timer_and_report(user_dir=args.user_dir, validation_result=result)
    elif args.cmd == "exec":
        ExecRun(args)
    elif args.cmd == "time":
        check_timer_and_report(user_dir=os.getcwd(), validation_result=None)
    elif args.cmd == "update":
        pullRun(args)
    elif args.cmd == "stats":
        show_stats(args)
    elif args.cmd == "recommend":
        recommendRun(args)
    else:
        argParser.print_help()

if __name__ == "__main__":
    main()
