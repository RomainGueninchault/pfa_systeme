Principe Général : Base d'exercices "téléchargeables" avec système d'auto-évaluation
                   Contrat(metadata) bien defini pour integrer facilement d'autre exercices

2 dépots minimum :
  - Le premier contient la base des exercices
  - Le deuxième contient un programme python permettant d'importer, executer et tester les exercices et évaluer l'utilisateur

Utilisation de la lib de M.Morandat ( Grader )

Dans un premier temps : entrainement pour le C ( peut-être d'autres langages dans le futur: java )


Dans la base d'exercices :
     - un fichier yaml(si je me rappelle bien comme M.Renault l'a utilise) pour avoir des info (compilation, test,..) on peut là probablement ajouter les autres info comme le temps, difficulte(selon utilisateur c'est mieux avec LLM??)
     - organisation en sous-dépôts (par langage par exemple)
     - tags par exercice ( dans un deuxième temps ) pour pouvoir organiser les exercices par types, difficulté...: Les tags depend de chaque utilisateur et n'ont pas universel? dans par LLM j'imagine
     - temps de résolution par exercice


Pour le système en python plusieurs commandes disponibles :

     - trainer -> liste des commandes dispos
     - trainer ls -> liste des exos disponibles ( par la suite on pourra ajouter des arguments pour sélectionner par tag ) / sans tag, trouver un moyen que la sortie soit lisible
     - trainer install exs -> installe la base d'exercies exs
     - trainer add ex dir -> rend disponible l'exercice ex dans le depot dir (qui doit être vide initialement)
     - trainer execute -> compile, execute et vérifie que l'exercice est réussi ( peut se décomposer en deux étapes : compilation puis execution + test)
     - trainer clean dir -> un rm -rf quoi
     
Le système doit également pouvoir vérifier le temps de résolution (timeout placé dans le yaml)


Le système global devra pouvoir vérifier automatiquement si un exercice est correct lors de la commande d'execution en utilisant la solution et une base de test. Cette base de test pourra être implémentée à la main au début pour des petits exercices (type min, max) pour voir si notre système fonctionne. Ils devront par la suite être automatisés avec des libs ( celle de M.Morandat en C par exemple) car trop long d'écrire 10 tests par exos à la main ( encore pire pour les exos incrémentaux).



Choses à faire une fois la base finie :
- Etendre à d'autres langages (java)
- utilisation des LLM pour adapter la difficulté / type d'exo ?
- mettre en place des tags + améliorer l'organisation / recherche des exercices
- standardisation des tags
- automatisation des écriture de tests par librairie
