# /executer — exécution réelle, contrôle de stabilité et validation V4

Cible : `[projet] [ID…]` ; sans ID, tous les tests du projet (projet facultatif s'il n'y en a qu'un).

1. **Tests encore `brouillon`** : `w2r stabilite <projet>` (3 passages ; un seul test :
   `w2r stabilite <projet> 3 --test "SC-002*" projets/<projet>/tests`). Seul un test **stable 3/3** peut
   être proposé à la V4.
   **Tests déjà actifs** : `w2r test <projet> --exclude brouillon projets/<projet>/tests` — contrôle de non-régression.
2. Pour chaque test : PASS / FAIL / SKIP, et pour un échec, le mot-clé et le message en cause.
   Lire `output.xml` (dans `projets/<projet>/reports/run/` ou `…/run/stabilite/passage_<i>/`) plutôt que
   deviner ; regarder les captures d'échec.
3. Comparer les **captures de fin** (`browser/screenshot/fin-*.png`, prises par `Terminer Le Test`) et
   d'échec avec les images du Word (`projets/<projet>/extracted/<doc>/images/`).
4. Un échec dû à une erreur du test (sélecteur, attente) : corriger, `w2r valider`, `w2r lint`,
   `w2r dryrun`, puis relancer `w2r stabilite`. Un échec dû à l'application : le signaler, ne pas
   « corriger » le test pour qu'il passe.

Présenter un tableau `ID | réussites (n/3) | cause | écart avec le Word`, puis demander, scénario par
scénario, l'accord V4. **Seulement après un accord explicite** : retirer le tag `brouillon` du `.robot`
et passer le `.feature` en `@statut:actif`, puis `w2r valider <projet>`.
Un SKIP pour session absente n'est pas un échec : renvoyer à `docs/credentials.md`.
