from arg import argParser
from importBase import importRun

def main():
    # recuper argument
    args = argParser.parse_args()
    if args.cmd == "import":
        importRun(args)

    elif args.cmd == "install":
        print("install command:", args.exs)

    else:
        argParser.print_help()

        
if __name__ == "__main__":
    main()
