# Méthode Word → Gherkin → Robot Framework

Référence unique, partagée par Claude Code et GitHub Copilot. Les commandes `/traduire`, `/valider`,
`/automatiser`, `/executer`, `/etat` (fichiers `procedures/<commande>.md`) en sont des étapes.

Suivre les étapes dans l'ordre. **S'arrêter à chaque validation humaine** (V1, V2, V4) et présenter
le rapport à l'utilisateur au lieu de continuer.

## Repères

- **Un projet = une application testée** : dossier `projets/<projet>/` (noté `<P>` ci-dessous). Le projet
  se déduit du chemin du Word ; sinon il est donné en argument (facultatif s'il n'y en a qu'un).
  Nouveau projet : `w2r nouveau-projet <nom>`, puis renseigner `<P>/projet.yaml` (URL, personas).
- **Tout s'exécute dans le conteneur Podman** : `.\w2r.ps1 <commande>`, noté `w2r` ; liste : `w2r aide`.
  `w2r.ps1` démarre la machine Podman si besoin ; s'il échoue encore, vérifier avec l'utilisateur que la
  machine est en mode rootful et l'image construite (README). Ne jamais installer Python, Robot ou un
  navigateur sur le poste.
- **Après chaque modification** d'un `.feature`, `.robot` ou `.resource` : `w2r valider` puis `w2r lint`,
  et corriger avant de continuer (Claude Code a aussi un hook ; Copilot n'en a pas).
- **Décisions déjà prises** : `commun/conventions.md` (tous projets) et `<P>/conventions.md` (ce projet).
  Elles ne se redemandent pas.

## 1. Extraire

`w2r extraire <P>/scenarios_word/<fichier>.docx` → `<P>/extracted/<fichier>/`.
- Lire `extraction.md`, puis **regarder chaque image** de `images/`.
- Lire `secrets_report.md`. S'il n'est pas vide, le signaler en premier à l'utilisateur
  (identifiants à changer). Ne jamais chercher les valeurs d'origine dans le .docx.

## 2. Écrire le pivot Gherkin `<P>/features/<ID>_<titre_court>.feature`

Un fichier par scénario du Word, un seul `Scénario:` par fichier. `<ID>` : l'identifiant du Word
(`SC-001`, `TC-12`…), sinon le prochain numéro libre `SC-xxx` du projet. Le Gherkin est en **français**
(`# language: fr`) et se lit comme une phrase métier : c'est ce que l'auteur du Word relira en V2.

```gherkin
# language: fr
@SC-004 @persona:gestionnaire @statut:brouillon @auto:total @clients @smoke
Fonctionnalité: Rechercher un client
  Source: Recette_CRM_v2.docx § 3.1 – Recherche client
  Images: image_03, image_04
  Objectif: vérifier qu'un client existant est retrouvé par son nom
  Raison auto: (seulement si @auto:partiel ou @auto:non — ce qui ne peut pas être automatisé)

  Contexte:
    Étant donné que le gestionnaire est connecté
    # mot-clé: Ouvrir Une Session Persona | origine: deduit | confiance: moyenne

  Scénario: Rechercher un client par son nom
    Quand il recherche le client "Dupont"
    # mot-clé: NOUVEAU: Rechercher Un Client | origine: tableau | confiance: haute
    Alors au moins "1" client est affiché
    # mot-clé: NOUVEAU: La Liste Des Clients Contient Au Moins | origine: legende | confiance: moyenne
    Et la fiche du premier client affiche "Dupont"
    # mot-clé: NOUVEAU: La Fiche Client Affiche | origine: deduit, image_04 | confiance: basse
    # nettoyage: NOUVEAU: Supprimer Le Client De Test

# Q1 | « la fiche du premier client » | action_vague | bloquant
#   question: « Vérifier que c'est le bon client » : sur quel champ ?
#   proposition: le nom affiché sur la fiche contient « Dupont »
#   réponse:
```

Règles d'écriture :
- **Tags de la Fonctionnalité** (obligatoires) : `@<ID>`, `@persona:<p>`, `@statut:brouillon`,
  `@auto:total|partiel|non`. Tags libres ensuite (en minuscules).
- **Description** : lignes `Clé: valeur`. `Source:` obligatoire (fichier § section du Word).
- **Étapes** : `Étant donné que` (état initial), `Quand` (action), `Alors` (résultat attendu), `Et`/`Mais`.
  Une étape = une intention, en phrase métier : **aucun terme technique** (sélecteur, URL, attribut).
  Chaque donnée est entre guillemets (`"Dupont"`, `"10"`) : une valeur = un argument du mot-clé, dans
  l'ordre (le validateur compare leur nombre aux arguments du mot-clé). Préconditions communes dans `Contexte:`.
- **Annotation** sous chaque étape : `# mot-clé: <Nom> | origine: <…> | confiance: <…>`
  - `mot-clé` : réutiliser un mot-clé de `commun/session.resource` ou `<P>/resources/metier.resource`,
    sinon `NOUVEAU: <Nom Du Mot Clé>`.
  - `origine` (une ou plusieurs, séparées par des virgules) : `texte`, `tableau`, `legende`, `deduit`, `image_NN`.
  - `confiance` : `haute` (écrit explicitement), `moyenne` (déduit d'une capture ou d'une légende),
    `basse` (interprétation : créer aussi une question sur cette étape).
- **Nettoyage** : `# nettoyage: <mot-clé>` en fin de scénario (devient le `[Teardown]`).
- **Questions** en fin de fichier : `# Qn | « extrait de l'étape » | catégorie | bloquant|non bloquant`.
  L'extrait entre « » doit se trouver dans le texte d'**une seule** étape (sans « Quand/Alors… ») ;
  `-` pour une question sur tout le scénario. Pas de numéro d'étape : il change si on insère une étape.

Créer une **question** (avec `proposition` par défaut, déjà appliquée dans les étapes) pour chacun de
ces cas, sauf si les conventions y répondent déjà :

| Catégorie | Signal dans le Word |
|---|---|
| `attendu_manquant` | case « Résultat attendu » vide |
| `action_vague` | « vérifier que c'est OK », « valider », « la bonne case » |
| `donnee_manquante` | valeur à saisir non précisée, URL de l'application absente |
| `contradiction_texte_image` | la capture montre autre chose que le texte (ou que l'appli réelle) |
| `non_deterministe` | « au hasard », publicité, données qui changent |
| `etapes_fusionnees` | paragraphe libre enchaînant plusieurs actions |
| `dependance` | « comme dans SC-xxx », « sinon le test suivant plante » |
| `technique` | limite d'automatisation (captcha, MFA, fichier à télécharger…) |
| `securite` | identifiant ou marqueur `<MOT_DE_PASSE_n>` présent |

Marquer `bloquant` **seulement** si la proposition par défaut risque de tester la mauvaise chose : les
questions non bloquantes sont repliées dans la fiche et acceptées par défaut. Viser peu de questions.
Remplacer tout compte par un `persona` déclaré dans `<P>/projet.yaml` (nom de variable d'environnement
uniquement ; voir `docs/credentials.md` pour choisir entre session et formulaire).

## 3. Valider (V1 puis V2)

`w2r valider <projet>` jusqu'à 0 erreur. Puis présenter les questions **bloquantes** de
`<P>/reports/validation_1.md` et **attendre les réponses** (`/valider`). L'utilisateur répond dans le chat,
dans `validation_1.md`, ou l'auteur dans la fiche Word (`w2r fiche-word <projet>` →
`<P>/reports/validation_<cahier>.docx`, relue par `w2r import-word <fiche>`).

Reporter les réponses sur la ligne `réponse:`, ajuster les étapes, passer `@statut:a_valider`.
Une réponse qui vaut pour tout le projet va aussi dans `<P>/conventions.md` (pour tous les projets :
`commun/conventions.md`). Ensuite, faire relire `<P>/reports/validation_2.md` (ou la partie 2 de la fiche
Word) par l'auteur ; à son accord explicite, `@statut:valide`.

## 4. Localisateurs et code (seulement pour `@statut:valide`, jamais pour `@auto:non`)

1. `URL_ACCUEIL` et les réglages de l'application sont dans `<P>/projet.yaml`. URL absente : la demander
   (ou reprendre la réponse V1).
2. **Relevé** avec le serveur MCP `playwright` (Chromium sans fenêtre, dans le conteneur, comme les tests) :
   `browser_snapshot` à chaque écran du scénario, comparer avec les captures du Word (différence →
   question `contradiction_texte_image`). Persona connecté : la session doit avoir été préparée par
   l'utilisateur (docs/credentials.md) ; ne jamais saisir d'identifiant soi-même.
3. Localisateurs : `<P>/resources/locators.resource`, y compris `PAGE_PRETE` et `INDICATEUR_CONNECTE`
   (attendus par `commun/session.resource`). Priorité : rôle + nom accessible > attribut stable > classe
   stable, jamais de XPath positionnel ; `# À CONFIRMER` si non relevé.
4. **Essayer chaque mot-clé avant de l'écrire** avec le serveur MCP `robotframework` (rf-mcp) :
   ouvrir une session Browser, exécuter pas à pas les mots-clés Browser prévus (clic, attente, assertion)
   sur l'appli réelle, y compris les cas non déterministes (publicité, bandeau en différé). Un mot-clé
   qui ne passe pas ici ne s'écrit pas.
5. Mots-clés métier : `<P>/resources/metier.resource` (il importe `projet.yaml`, `commun/session.resource`
   et `locators.resource`). Un mot-clé = une intention, avec ses attentes et assertions. Pas de `Sleep`.
   Un mot-clé utile à tous les projets va dans `commun/session.resource`. Retirer ensuite le préfixe
   `NOUVEAU:` des annotations.
6. Test : `<P>/tests/<ID>_<titre_court>.robot`, un cas de test par `.feature` :
   - `Resource  ../resources/metier.resource` ;
   - `[Documentation]` : titre, `Source:` et chemin du `.feature` ;
   - `Test Tags` : `projet:<projet>`, `<ID>`, `persona:<p>`, les tags libres, `brouillon` ;
   - étapes dans l'ordre du Gherkin, préfixes traduits : `Étant donné que` → `Given`, `Quand` → `When`,
     `Alors` → `Then`, `Et` → `And`, `Mais` → `But` ; les valeurs entre guillemets deviennent les arguments ;
   - `Suite Setup  Démarrer Le Navigateur` ; `Test Teardown  Terminer Le Test` (capture finale) ;
     s'il y a un nettoyage : `[Teardown]` avec les mots-clés `# nettoyage:` puis `Terminer Le Test`.
7. V3 automatique — tout doit passer : `w2r valider <projet>` (traçabilité, ordre, arguments), `w2r lint`,
   `w2r dryrun <projet>`.

## 5. Exécuter (V4)

1. `w2r stabilite <projet>` : les tests encore `brouillon` sont exécutés **3 fois** ; seul un test stable
   (3/3) est proposé à la V4. Un test instable : analyser les passages en échec
   (`<P>/reports/run/stabilite/`), corriger, recommencer.
2. Ouvrir le `log.html` d'un passage, comparer les **captures de fin** (`Terminer Le Test`) et d'échec avec
   les images du Word, présenter le résultat.
3. À l'accord explicite de l'utilisateur seulement : retirer le tag `brouillon` du `.robot` **et** passer
   le `.feature` en `@statut:actif` (le validateur vérifie que les deux vont ensemble). Les tests actifs
   se relancent avec `w2r test <projet> --exclude brouillon projets/<projet>/tests`.

## Ne jamais

- écrire, afficher ou demander un mot de passe, un jeton ou un fichier de session ; lire `.env` ou `.auth/` ;
- inventer un résultat attendu sans question associée ;
- mettre un localisateur ou un mot-clé Browser dans `<P>/tests/` ;
- écrire du code Robot pour un scénario qui n'est pas `@statut:valide` (sauf demande explicite) ;
- considérer un dry-run « PASS » comme une preuve que le test marche (il ne vérifie ni les sélecteurs ni le JavaScript).
