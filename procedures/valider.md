# /valider — reporter les réponses V1 / l'accord V2 et faire avancer les statuts

Réponses de l'utilisateur : l'argument de la commande, par exemple `SC-001 Q1: refuser, Q3: ok`,
`SC-001 conforme`, `tout` ou `tout conforme`, éventuellement précédé du projet (`youtube SC-001 Q1: ok`) ;
le projet est facultatif s'il n'y en a qu'un.

Sources des réponses, dans cet ordre :
1. l'argument ci-dessus ;
2. une fiche Word remplie (`projets/<projet>/reports/validation_*.docx` modifiée par l'auteur, ou un chemin
   donné) : `w2r import-word <fiche.docx>` recopie les réponses et affiche les avis « Conforme » ;
3. les lignes « Réponse : » remplies dans `projets/<projet>/reports/validation_1.md`, puis les cases cochées
   dans `validation_2.md`.

Interprétation :
- « ok », « d'accord », « proposition » sur une question = accepter la proposition par défaut ;
- `tout` = accepter la proposition de **toutes** les questions encore ouvertes, bloquantes comprises :
  les lister avant d'écrire (l'utilisateur doit voir ce qu'il accepte) ;
- `conforme` / `tout conforme` = accord V2 de l'auteur pour ce(s) scénario(s).

Pour chaque `.feature` concerné :
1. Écrire chaque réponse sur la ligne `réponse:` de la question (« proposition acceptée » pour un accord) ;
   si elle diffère de la proposition, corriger les étapes et leurs annotations (une réponse peut créer
   une nouvelle question). Une réponse valable pour tout le projet va aussi dans `projets/<projet>/conventions.md`
   (pour tous les projets : `commun/conventions.md`).
2. Statut :
   - `@statut:brouillon` → `@statut:a_valider` quand plus aucune question bloquante n'est ouverte ;
   - `@statut:a_valider` → `@statut:valide` seulement avec l'accord V2 explicite de l'auteur.
3. `w2r valider <projet>` jusqu'à 0 erreur (régénère les fiches) ; `w2r fiche-word <projet>` si des
   questions restent ouvertes.

Présenter : le tableau d'avancement, les questions encore ouvertes, ce qui a changé dans les étapes.
Si des scénarios sont `valide` : proposer `/automatiser`. Si des scénarios passent en `a_valider` :
indiquer que la relecture V2 est prête (validation_2.md ou partie 2 de la fiche Word).
Ne jamais passer un scénario en `valide` sans accord explicite de l'auteur.
