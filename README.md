# Trainer - Système d'entraînement

Un système d'entraînement en ligne de commande pour gérer et exécuter des exercices de programmation avec timer et validation.

## Installation

```bash
pip install -e .
```

Cette commande installe le projet en mode développement. Les dépendances requises (PyYAML) seront automatiquement installées.

## Utilisation

Après installation, la commande `trainer` est disponible globalement.



## Workflow typique

1. **Importer les exercices**
   ```bash
   trainer import https://github.com/user/exercices.git
   ```

2. **Lister les exercices disponibles**
   ```bash
   trainer ls
   ```

3. **Exécuter un exercice**
   ```bash
   trainer exec min_1
   ```

4. **Résoudre l'exercice** dans le shell interactif

Remplir la fonction dans le fichier `skeleton.c`

5. **Valider la solution**
   ```bash
   trainer check
   ```

---

## Aide

Pour afficher l'aide générale :
```bash
trainer -h
```

Pour l'aide d'une commande spécifique :
```bash
trainer import -h
trainer ls -h
trainer install -h
trainer exec -h
trainer check -h
```

---
