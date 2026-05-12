import argparse

argParser = argparse.ArgumentParser(prog='trainer')
subparsers = argParser.add_subparsers(title='command',dest='cmd',help='sub-command help',required=True)



parser_import=subparsers.add_parser('import',help="add a new repository")
parser_import.add_argument('url',help="git url of the respository")
parser_import.add_argument("--base-dir", default="~/.trainer", help="Base directory for import")

parser_install = subparsers.add_parser('install', help="Install an exercice")
parser_install.add_argument("--base-dir", default="~/.trainer", help="Base directory for exercises")
parser_install.add_argument('exs', help="name of exercice")
parser_install.add_argument("--user-dir", default=None, help="User directory for installation")

parser_ls = subparsers.add_parser('ls', help="List exercises in the base directory")

parser_ls.add_argument("--base-dir", default="~/.trainer", help="Base directory where repositories are installed")
parser_ls.add_argument("--tag", default="", help="Filter exercises by tag substring")
parser_ls.add_argument("-d", "--done", action="store_true", help="Show exercises that are already done (by default they are hidden)")
parser_ls.add_argument("-r", "--repo", default="", help="Filter exercises by repository name (e.g., exercices2A)")


parser_exec = subparsers.add_parser('exec', help="Open a temporary exec shell for an exercise")
parser_exec.add_argument("--base-dir", default="~/.trainer", help="Base directory for exercises")
parser_exec.add_argument('exs', help="exercise alias (ex: min_1, sum_2)")

parser_check = subparsers.add_parser('check', help="Validate solution in current or provided directory")
parser_check.add_argument("--base-dir", default="~/.trainer", help="Base directory for exercises")
parser_check.add_argument("--user-dir", default=None, help="Directory containing the exercise to validate")


parser_update = subparsers.add_parser('update', help="Update an existing exercise")
parser_update.add_argument("--base-dir", default="~/.trainer", help="Directory containing the exercise to update")

parser_stats = subparsers.add_parser('stats', help="List the exercises that have been done and failed")
parser_stats.add_argument("--filter", default="", help="Filter the stats by status")

parser_recommend = subparsers.add_parser('recommend', help="Recommend exercises from a reference exercise")
parser_recommend.add_argument('reference_alias',help="Alias de l'exercice de référence")
parser_recommend.add_argument("--base-dir",default="~/.trainer",help="Base directory for exercises")
parser_recommend.add_argument("--top-k",type=int,default=5,help="Nombre de recommandations")
parser_recommend.add_argument("--include-done",action="store_true",help="Inclure aussi les exercices déjà faits")
parser_recommend.add_argument("--allow-lower-difficulty",action="store_true",help="Ne pas filtrer les difficultés inférieures")
parser_recommend.add_argument("--min-common-tags",type=int,default=1,help="Nombre minimum de tags en commun")



parser_recommend.add_argument("--ai", action="store_true", help="Utiliser la recommandation IA (sentence-transformers) au lieu de Jaccard strict")
parser_recommend.add_argument("--tag-weight", type=float, default=0.6, help="Poids de la similarité des tags (mode IA)")
parser_recommend.add_argument("--desc-weight", type=float, default=0.4, help="Poids de la similarité des descriptions (mode IA)")
parser_recommend.add_argument("--tag-threshold", type=float, default=0.65, help="Seuil cosinus pour considérer deux tags équivalents (mode IA)")
 
# --- Auto-tagging ---
parser_tag = subparsers.add_parser(
    "tag-suggest",
    help="Suggérer automatiquement des tags libres et une difficulté avec un LLM",
)

parser_tag.add_argument(
    "alias",
    nargs="?",
    default=None,
    help="Alias de l'exercice. Si omis, traite tous les exercices.",
)

parser_tag.add_argument(
    "--base-dir",
    default="~/.trainer",
    help="Base directory for exercises",
)

parser_tag.add_argument(
    "--repo",
    default="",
    help="Ne traiter que les exercices d'un repo donné si alias est omis",
)

parser_tag.add_argument(
    "--apply",
    action="store_true",
    help="Écrire les tags proposés et difficulty dans config.yml",
)

parser_tag.add_argument(
    "--skip-existing",
    action="store_true",
    help="Ne pas remplacer les tags ou difficulty déjà présents",
)
