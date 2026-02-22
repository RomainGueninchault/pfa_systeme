import argparse

argParser = argparse.ArgumentParser(prog='trainer')
subparsers = argParser.add_subparsers(title='command',dest='cmd',help='sub-command help',required=True)


parser_import=subparsers.add_parser('import',help="add a new repository")
parser_import.add_argument('url',help="git url of the respository")
parser_import.add_argument("--base-dir", default="~/.base")

parser_install = subparsers.add_parser('install', help="Install an exercice")
parser_install.add_argument('exs', help="name of exercice")

if __name__ == '__main__':
    args = argParser.parse_args()
    print(args)
