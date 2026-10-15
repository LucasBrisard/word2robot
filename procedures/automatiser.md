# /automatiser — relevé des localisateurs, essai des mots-clés, code Robot (étape 4 + V3)

Cible : `[projet] [ID…]` ; sans ID, tous les `.feature` du projet en `@statut:valide` sans `.robot`
(projet facultatif s'il n'y en a qu'un).

- Ne traiter que des `.feature` en `@statut:valide`. Pour un autre statut, expliquer ce qui manque
  (`/valider`) et ne rien coder, sauf si l'utilisateur demande explicitement un brouillon.
- Ignorer les `.feature` en `@auto:non` (les lister avec leur « Raison auto »).
- Si un scénario utilise un persona connecté dont la session n'est pas prête (`.auth/<projet>/<persona>.json`
  absent : vérifier l'existence du fichier sans le lire), s'arrêter et renvoyer l'utilisateur à
  `docs/credentials.md` (préparation de session).

Suivre `procedures/methode.md`, étape 4, dans cet ordre :
1. relevé avec le serveur MCP `playwright` ;
2. **essai de chaque mot-clé** avec le serveur MCP `robotframework` (rf-mcp) sur l'appli réelle, avant
   de l'écrire — y compris les cas aléatoires (publicités, bandeaux en différé) ;
3. localisateurs, mots-clés métier, réglages dans `projet.yaml`, test `.robot` (tag `brouillon`, teardown
   `Terminer Le Test`) ;
4. V3 : `w2r valider <projet>`, `w2r lint` (sinon `w2r format` puis `w2r lint`), `w2r dryrun <projet>`.

Présenter : les fichiers créés, les localisateurs marqués `# À CONFIRMER`, ce que l'essai rf-mcp a
révélé, les écarts constatés entre le Word et l'appli (ajoutés en questions), le résultat de la V3.
Proposer `/executer`.
