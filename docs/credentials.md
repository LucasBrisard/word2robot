# Gestion des credentials

**Principe : les scénarios manipulent des personas, jamais des identifiants.** Un persona est un rôle
(`visiteur_anonyme`, `utilisateur_connecte`, `gestionnaire`…). Les secrets restent hors des
`.feature`, des prompts de l'IA et des logs.

## Quel mécanisme pour quel persona ?

| L'application… | Ce que vous faites | Ce que vous fournissez |
|---|---|---|
| ne demande pas de connexion | rien | rien |
| se connecte par SSO / Google / MFA | vous vous connectez **vous-même** une fois dans un navigateur ; la session est enregistrée | le fichier `.auth/<projet>/<persona>.json` |
| a un formulaire identifiant + mot de passe | vous mettez le compte de test dans `.env` | `<PERSONA>_USER` et `<PERSONA>_PASSWORD` (persona préfixé par le projet : `CRM_GESTIONNAIRE`) |

Le nom du persona vient du `.feature` (`@persona:…`) ; l'agent (Claude ou Copilot) le déclare dans `projets/<projet>/projet.yaml`.
Sans session ni identifiants, le test est **ignoré** (SKIP), pas en échec.

## Préparer une session (SSO, MFA)

C'est la seule étape hors conteneur, car il faut un navigateur visible : elle demande Node.js et Edge sur le poste.

```bash
npx -y playwright@latest codegen --channel msedge --save-storage=.auth/<projet>/<persona>.json https://url-de-l-appli
```

Connectez-vous dans la fenêtre avec le **compte de test**, puis fermez-la : la session est enregistrée
dans `.auth/`. À refaire quand la session expire. L'agent ne voit jamais le mot de passe ;
les tests réutilisent ce fichier. Pour un relevé connecté, ajouter
`"--storage-state", "/work/.auth/<projet>/<persona>.json"` à la commande `mcp-playwright` (dans `.mcp.json` et `.vscode/mcp.json`).

Si Google refuse la connexion (« navigateur non sécurisé »), utiliser un compte de test dédié ou une
appli de recette avec authentification propre.

## Formulaire classique (`.env`)

Copier `env.example` en `.env` et renseigner, pour chaque persona concerné :

```
GESTIONNAIRE_USER=compte.de.test
GESTIONNAIRE_PASSWORD=…
```

Le conteneur charge `.env` à son démarrage (`.\w2r.ps1 stop` après une modification). Le mot-clé `Se Connecter Par Formulaire` saisit le mot de passe
avec `Fill Secret`, qui ne l'écrit pas dans `log.html`.

## Garde-fous automatiques

- `extract_docx.py` masque les secrets du texte (et des captures grâce à l'OCR de l'image).
- `valider_features.py` refuse un `.feature` qui contient un identifiant ou un marqueur de secret.
- Hook Claude Code (`tools/hook_validation.py`) : bloque un `.robot` avec un secret en dur.
- `.claude/settings.json` interdit à Claude de lire `.env`, `.auth/` et les `.docx` bruts (Copilot : règle écrite dans AGENTS.md).
- Ne pas diffuser `.env`, `.auth/`, ni les `scenarios_word/` et `extracted/` des projets : un Word peut contenir un mot de passe.

## Si un secret est trouvé dans un Word

Le considérer comme compromis : le faire changer, le retirer du Word, et ne pas diffuser le Word d'origine.
