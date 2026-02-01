import argparse

argParser = argparse.ArgumentParser(prog='trainme')
subparsers = argParser.add_subparsers(title='command',dest='cmd',help='sub-command help',required=True)


parser_run=subparsers.add_parser('run',help="run an exercice")
parser_run.add_argument('exercice',help="name of the exercice")
parser_run.add_argument("-d", "--dir",type=str, help="directory where to deploy exercice")
parser_run.add_argument("-t", "--tmp",action='store_true', help="deploy exercice to a temporary directory")

parser_run=subparsers.add_parser('import',help="add a new repository")
parser_run.add_argument('url',help="git url of the respository")

parser_run=subparsers.add_parser('config',help="print configuration")

parser_run=subparsers.add_parser('update',help="update stored repositories")


parser_run=subparsers.add_parser('check',help="check if current exercice is correct")

parser_run=subparsers.add_parser('list',help="list repositories")

if __name__ == '__main__':
    args = argParser.parse_args()
    print(args)
