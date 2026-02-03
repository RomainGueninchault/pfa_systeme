# bibliotique
**argparse:** pour analyser les arguments (mieux que sys.argv[]) car genere -h (exemple tm_args.py)
**yaml:** pour lire yaml
# Version 1
## Installation programme
rendre le programme par tout (sans faire python3 trainer dans le repertoir ou se situer trainer.py)
avec [pip](https://packaging.python.org/en/latest/guides/section-build-and-publish/)

## Structure des exercices
Une base est un répertoire contenant un fichier YAML spécifique nommé `trainer.yaml`. Ce fichier décrit les informations générales de la base (nom, auteur, version, description, tags, etc.) ainsi que, si nécessaire, des paramètres par défaut applicables aux exercices de la base.
L’organisation est récursive: 
    - baseParent → base base …
    - base → base base … | exercices
    - Un exercice est un répertoire contenant les fichiers et `exercise.yaml`, et bases contient des sous bases

## Installation des depots
on installer les bases via leurs URL dans cette fichier `~/.local/share/trainer/` afin de les centraliser.

## Lister les depots
1. on lister les bases installer dans `~/.local/share/trainer/`, on parcours l'arborescente pour lire les `exercice.yaml`
2. on peut s'insperer de `apt` qui utilise `/etc/apt/source.list`
`trainer -ls`

## recuperer exercice
1. Je pense ca veut mieux d'avoir une mini database dans `~/.local/share/trainer/` pour acceler la verification que cette exo existe et aussi le trouver, ou bien une `grep -nri "name"` par exemple pour voir si exo exist et ou?
2. on appliquer **Compilation** dans le yaml comme l'exemple de la base **Basic**, pour enlever les sources code des tests.
`trainer install exo_name`

## Si on installe plusieurs dépots et que deux exos ont le meme nom ?
pour lister les exercices, on affiches les deux noms avec leurs options, mais pour installer on peut utilise une carracteristique dans `trainer.yaml` comme le compilateur c++

## Notion du temps
pas une priorite pour cette version?

## Dépendences systèmes dans les fichiers yaml ( google test, valgrind, gdb...), quitte à ce que l'outil explique que le système est pas à jour.
avant d'installer un exercice on lit `exercice.yaml` section dependencies pour verifier.

## shell
                              
