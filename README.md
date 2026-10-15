# word2robot

Transformer des cahiers de recette Word (texte approximatif + captures d'écran) en tests
Robot Framework (Browser/Playwright), avec un agent de code — **Claude Code ou GitHub Copilot** — et des
validations humaines à chaque étape. Plusieurs applications : un dossier par application dans `projets/`.
Tout l'outillage tourne dans un conteneur **Podman**.

```
Word ──/traduire──▶ Gherkin (.feature) ──/valider──▶ validé par l'auteur ──/automatiser──▶ .robot ──/executer──▶ actif
         V1 : questions bloquantes   V2 : relecture métier          V3 : lint + dry-run      V4 : 3 passages + captures
```

## Installation (une fois)

Prérequis sur le poste : **Podman** et un agent (Claude Code, ou VS Code + GitHub Copilot).

```bash
winget install -e --id RedHat.Podman
```
```bash
podman machine init --rootful
```

**`--rootful` est indispensable sous Windows** : sinon le conteneur ne peut pas modifier les fichiers du
projet. Machine déjà créée : `podman machine stop`, `podman machine set --rootful`, puis reconstruire l'image.
Ensuite, dans le dossier du projet (la machine Podman est démarrée automatiquement si besoin) :

```powershell
.\w2r.ps1 build
```
## Utilisation

1. Nouvelle application : `.\w2r.ps1 nouveau-projet facturation`, puis renseigner l'URL dans
   `projets/facturation/projet.yaml`.
2. Copier le cahier Word dans `projets/<projet>/scenarios_word/`.
3. Dans l'agent (Claude Code, ou le chat Copilot en mode Agent) :

| Commande | Ce qu'elle fait | S'arrête sur |
|---|---|---|
| `/traduire projets/facturation/scenarios_word/Recette.docx` | extraction, masquage des secrets, un `.feature` par scénario, fiche Word pour l'auteur | les questions bloquantes (V1) |
| `/valider SC-001 Q1: refuser, Q3: ok` | reporte les réponses, fait avancer le statut | la relecture V2 par l'auteur |
| `/valider tout` | accepte toutes les propositions par défaut (après les avoir listées) | la relecture V2 |
| `/valider SC-001 conforme` | accord de l'auteur du Word → `@statut:valide` | — |
| `/automatiser facturation` | relevé sur l'appli, essai des mots-clés, `.robot`, lint + dry-run | le résultat de la V3 |
| `/executer facturation` | 3 passages des nouveaux tests, captures de fin comparées au Word | l'accord V4 (→ test actif) |
| `/etat` | avancement de tous les projets et prochaine commande | — |

Le nom du projet est facultatif quand il n'y en a qu'un. L'auteur du Word peut répondre **dans Word** : la fiche
`projets/<projet>/reports/validation_<cahier>.docx` est relue par `/valider`.

## Organisation

```
commun/          ce qui sert à toutes les applications (mots-clés de base, réglages navigateur, conventions)
projets/<appli>/ une application : projet.yaml, conventions.md, scenarios_word/, features/, resources/, tests/, reports/
modele/          squelette d'un nouveau projet
procedures/      méthode et commandes, communes à Claude et Copilot
tools/           scripts (extraction, validateur, fiche Word, stabilité) exécutés dans le conteneur
```

Statuts d'un scénario : `brouillon` → `a_valider` (V1) → `valide` (V2) → `actif` (V4, relancé par
`.\w2r.ps1 test <projet> --exclude brouillon projets/<projet>/tests`). Format du Gherkin
et règles : [procedures/methode.md](procedures/methode.md) ; règles des agents : [AGENTS.md](AGENTS.md) ;
identifiants : [docs/credentials.md](docs/credentials.md).

Ne pas diffuser les Word, leur extraction, les sessions (`.auth/`) ni `.env` : ils peuvent contenir des
identifiants. Modèle de `.env` (applis à formulaire de connexion seulement) : `env.example`.
