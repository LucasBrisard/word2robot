# Conventions communes à tous les projets

Décisions qui valent pour **toutes** les applications. L'agent (Claude ou Copilot) les applique sans
reposer la question ; il ne crée une question que si un cahier Word les contredit. Les décisions propres
à une application sont dans `projets/<projet>/conventions.md`.

| # | Sujet | Décision | Origine |
|---|---|---|---|
| G1 | Navigateur | Chromium sans fenêtre, 1366×900, dans le conteneur (le « Chrome » d'un Word est accepté ainsi) | youtube SC-001 Q7 |
| G2 | Langue | Interface forcée en français (`locale=fr-FR`, et paramètre de langue de l'appli s'il existe) | youtube SC-001 Q7 |
| G3 | Cookies | Toujours refuser (« Tout refuser ») ; sans bandeau, ne rien faire | youtube SC-001 Q2, Q3 |
| G4 | Non-déterminisme | Publicités, directs, données changeantes : on les neutralise (attendre, exclure, fixer la donnée), on ne les vérifie pas | youtube SC-001 Q6, SC-002 Q1 |
| G5 | Indépendance | Un test refait lui-même ses préconditions (« comme dans SC-xxx » = rejouer les étapes, pas dépendre de l'autre test) | youtube SC-002 Q5 |
| G6 | Nettoyage | Toute donnée créée est retirée en fin de test, même en échec, sans erreur si elle n'existe plus | youtube SC-003 Q5 |
| G7 | Environnement | Si le Word ne précise pas l'environnement : demander un environnement de recette avec des données de test fixes (première question d'un nouveau projet) | — |
