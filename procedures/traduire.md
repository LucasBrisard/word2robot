# /traduire — Word → Gherkin (étapes 1 à 3), jusqu'aux questions V1

Entrée : un fichier `projets/<projet>/scenarios_word/<fichier>.docx` (argument de la commande) ; le projet
se déduit de son chemin.

- Argument = un nom de projet, ou rien : prendre les `.docx` de `projets/<projet>/scenarios_word/` (de tous
  les projets si rien) qui n'ont pas encore de dossier dans `extracted/` ; s'il n'y en a aucun, demander le fichier.
- Si le Word n'est dans aucun projet : demander pour quelle application il est ; si le projet n'existe pas,
  le créer avec `w2r nouveau-projet <nom>` (accord de l'utilisateur), puis demander de copier le Word dans
  son `scenarios_word/` (ne pas lire un .docx ailleurs).

Suivre `procedures/methode.md`, étapes 1 à 3 : `w2r extraire` → lecture du texte ET de chaque image →
lecture des conventions (commune et du projet) → un `.feature` par scénario → `w2r valider <projet>`
jusqu'à 0 erreur → `w2r fiche-word <projet>` (fiche Word pour l'auteur).

Puis **s'arrêter** et présenter, dans cet ordre :
1. les secrets détectés (`secrets_report.md`), s'il y en a ;
2. le tableau d'avancement affiché par le validateur ;
3. les questions **bloquantes**, avec leur proposition par défaut ; pour les non bloquantes, seulement
   leur nombre (« acceptées par défaut sauf objection, détail dans reports/validation_1.md ») ;
4. la suite : « Répondez ici, dans projets/<projet>/reports/validation_1.md ou dans la fiche Word
   projets/<projet>/reports/validation_<cahier>.docx, puis /valider (ou /valider tout) ».
