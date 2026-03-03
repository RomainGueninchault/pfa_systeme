import argparse

argParser = argparse.ArgumentParser(prog='trainer')
subparsers = argParser.add_subparsers(title='command',dest='cmd',help='sub-command help',required=True)



parser_import=subparsers.add_parser('import',help="add a new repository")
parser_import.add_argument('url',help="git url of the respository")
parser_import.add_argument("--base-dir", default="~/.base", help="Base directory for import")

parser_install = subparsers.add_parser('install', help="Install an exercice")
parser_install.add_argument("--base-dir", default="~/.base", help="Base directory for exercises")
parser_install.add_argument('exs', help="name of exercice")
parser_install.add_argument("--user-dir", default=None, help="User directory for installation")

parser_ls = subparsers.add_parser('ls', help="List exercises in the base directory")
parser_ls.add_argument("--base-dir", default="~/.base", help="Base directory for exercises")
parser_ls.add_argument("--tag", default=None, help="Filter exercises by tag")

parser_check = subparsers.add_parser('check', help="Check an exercice")
parser_check.add_argument("--user-dir", default=None, help="Directory where the exercice is installed")

parser_time  = subparsers.add_parser('time', help="Check the time elapsed and the time remaining for the exercice. Must be in the directory of the exercice")

if __name__ == '__main__':
    args = argParser.parse_args()
    print(args)
