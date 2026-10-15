# word2robot — Scénarios Word → Gherkin → Robot Framework

Instructions pour les agents de code (GitHub Copilot, Claude Code, autres). Claude Code les lit via
`CLAUDE.md`, Copilot directement. Projet local (pas de Git).

Outil de traduction de cahiers de recette Word (texte flou + captures) en tests Robot Framework
(library **Browser**/Playwright), via un pivot **Gherkin** en français, pour **plusieurs applications** :
un dossier `projets/<projet>/` par application. Méthode complète : **[procedures/methode.md](procedures/methode.md)**.
Décisions déjà prises : `commun/conventions.md` (tous projets) et `projets/<projet>/conventions.md`.

## Pipeline (ne jamais sauter d'étape)

| # | Étape | Commande | Outil | Validation |
|---|---|---|---|---|
| 1 | Extraction + masquage des secrets | `/traduire` | `w2r extraire projets/<p>/scenarios_word/X.docx` | lire `secrets_report.md` |
| 2 | Pivot Gherkin (1 `.feature` par scénario) | `/traduire` | l'agent, à partir de l'extraction + images | `w2r valider` → **V1 humaine** : questions bloquantes |
| 3 | Relecture métier | `/valider` | fiches `validation_1/2.md` ou fiche Word (`w2r fiche-word`) | **V2 humaine** (l'auteur du Word) |
| 4 | Localisateurs + code `.robot` | `/automatiser` | MCP `playwright` (relevé), MCP `robotframework` (essai), puis `resources/` et `tests/` du projet | **V3 auto** : `w2r valider`, `w2r lint`, `w2r dryrun` |
| 5 | Exécution réelle | `/executer` | `w2r stabilite` (3 passages), `w2r test` | **V4 humaine** : log.html et captures de fin vs captures du Word |

`/etat` donne l'avancement de chaque projet et la prochaine commande. Les commandes sont décrites dans
`procedures/<commande>.md` (Claude : `.claude/commands/`, Copilot : `.github/prompts/`, mêmes procédures).

Statuts (tag `@statut:` du `.feature`) : `brouillon` → `a_valider` (V1 répondue) → `valide` (V2 faite)
→ `actif` (V4 faite : le `.robot` n'a plus le tag `brouillon`, il est relancé par `w2r test`).
Le validateur vérifie la cohérence.

## Arborescence

```
commun/                 session.resource (navigateur, personas, capture de fin), commun.yaml, conventions.md
projets/<projet>/       une application testée :
  projet.yaml             URL, personas, réglages (aussi variables Robot)
  conventions.md          décisions propres à l'application
  scenarios_word/         cahiers Word (peuvent contenir des secrets : ne pas les diffuser)
  extracted/              extraction texte + images (régénérable)
  features/               pivot Gherkin <ID>_<titre>.feature
  resources/              locators.resource (localisateurs) + metier.resource (mots-clés métier)
  tests/                  <ID>_<titre>.robot, un cas de test par .feature
  reports/                fiches V1/V2 (.md), fiche Word pour l'auteur, résultats d'exécution (run/)
modele/                 squelette copié par « w2r nouveau-projet <nom> »
procedures/             méthode et commandes, communes à tous les agents
tools/                  scripts Python exécutés dans le conteneur (via w2r)
```

## Commandes : tout passe par Podman

**Python, Robot, Chromium et les serveurs MCP ne sont pas installés sur le poste : ils sont dans l'image
Podman.** Point d'entrée unique : `.\w2r.ps1 <commande>`, noté `w2r`. `[projet]` est facultatif quand il n'y a qu'un projet.

```
w2r build                           # construire l'image (une fois, puis si Containerfile / requirements changent)
w2r nouveau-projet <nom>            # créer projets/<nom>/ depuis modele/
w2r extraire projets/<p>/scenarios_word/X.docx
w2r valider [projet]                # Gherkin, secrets, catalogue, arguments, traçabilité, ordre, statuts
w2r fiche-word [projet]             # fiche Word pour l'auteur ; w2r import-word <fiche> pour la relire
w2r lint                            # robocop check + format --check (w2r format pour corriger)
w2r dryrun [projet]                 # robot --dryrun --exitonerror
w2r stabilite [projet] [n]          # n passages (3) des tests « brouillon » avant V4
w2r test [projet] [args robot]      # exécution réelle → projets/<p>/reports/run
w2r lock                            # figer les versions Python (requirements.lock) puis w2r build
w2r stop                            # arrêter le conteneur (après une modification de .env)
```

`w2r.ps1` démarre la machine Podman si elle est arrêtée. S'il échoue encore : vérifier avec l'utilisateur
que la machine existe en mode rootful (`podman machine init --rootful`, voir README) et que l'image est
construite (`w2r build`) ; ne jamais installer Python ou un navigateur sur le poste. Serveurs MCP (dans le
conteneur) : `playwright` et `robotframework`, déclarés dans `.mcp.json` (Claude) et `.vscode/mcp.json` (Copilot).

## Règles

- **Secrets** : jamais dans le code, le Gherkin, les prompts ni les logs. Les scénarios utilisent des
  *personas* (`projets/<p>/projet.yaml` → nom de variable d'environnement). Voir `docs/credentials.md`.
  Ne jamais lire `.env`, `.auth/` ni un fichier storage state. Si l'appli demande une connexion,
  renvoyer l'utilisateur à `docs/credentials.md` et le laisser se connecter lui-même.
- **Projets séparés** : un projet ne référence jamais les fichiers d'un autre ; ce qui sert à plusieurs
  projets va dans `commun/`.
- **Gherkin** : phrases métier lisibles par l'auteur du Word, aucun terme technique (pas de sélecteur,
  d'URL technique ni de nom de mot-clé dans le texte des étapes ; ils vont dans les annotations `# mot-clé:`).
- **Tests** : uniquement des mots-clés métier, en Given/When/Then, dans l'ordre du `.feature`.
  Aucun localisateur ni mot-clé Browser dans `tests/`.
- **Localisateurs** : dans `projets/<p>/resources/locators.resource` uniquement, relevés sur l'appli réelle
  avec le MCP `playwright`. Priorité : rôle + nom accessible > attribut stable (`name`, `aria-label`,
  `data-testid`) > classe stable. Jamais de XPath positionnel. Marquer `# À CONFIRMER` ce qui n'a pas pu
  être relevé.
- **Essai avant écriture** : chaque mot-clé est exécuté sur l'appli réelle avec le MCP `robotframework`
  avant d'être écrit ; un dry-run ne prouve pas qu'un test marche.
- **Attentes** : jamais de `Sleep`. Utiliser `Wait For Elements State`, `Wait For Function`, les assertions
  intégrées de Browser (`Get Element Count  sel  >=  10`).
- **Non-déterminisme** (pubs, données aléatoires, directs) : ne pas le vérifier, le neutraliser
  (attendre, fixer la donnée) et le documenter dans une question du `.feature`.
- **Stabilité** : un test n'est proposé à la V4 qu'après 3 passages réussis sur 3 (`w2r stabilite`).
- **Indépendance** : chaque test a son contexte, son setup et son nettoyage idempotent.
- **Traçabilité** : tags `projet:<p>` et `<ID>` + `[Documentation]` citant le fichier et la section du Word.
- **Ne pas inventer** : une information absente du Word devient une question avec une `proposition`,
  jamais une hypothèse silencieuse.
- **Contrôle continu** : après chaque modification d'un `.feature`, `.robot` ou `.resource`, lancer
  `w2r valider` et `w2r lint` (Claude Code a un hook qui le fait ; les autres agents doivent le lancer).
