#!/usr/bin/env python3
"""Contrôles automatiques des scénarios pivot Gherkin (projets/<p>/features/*.feature) + fiches de validation.

Format attendu (détaillé dans procedures/methode.md) :

    # language: fr
    @SC-001 @persona:visiteur_anonyme @statut:brouillon @auto:total
    Fonctionnalité: Rechercher une vidéo
      Source: Recette.docx § SC-001 – Rechercher une vidéo
      Images: image_01, image_02
      Objectif: vérifier que la recherche renvoie des résultats pertinents

      Scénario: Rechercher une vidéo
        Étant donné que le visiteur ouvre la page d'accueil
        # mot-clé: Ouvrir L Application | origine: tableau | confiance: haute
        ...
        # nettoyage: Retirer Le Favori

    # Q1 | « il refuse les cookies » | action_vague | non bloquant
    #   question: « Valider les cookies » = accepter ou refuser ?
    #   proposition: refuser
    #   réponse:

Une question est rattachée à l'étape dont le texte contient l'extrait entre « » (insensible à la casse),
ou à tout le scénario avec « - ». L'ancrage par texte résiste à l'insertion d'une étape.

Contrôles (code retour 1 si l'un échoue) :
  1. syntaxe Gherkin (parseur officiel Cucumber) ; tags @<ID> (ex. @SC-001, l'identifiant du Word),
     @persona:, @statut:, @auto: ; « Source: »
  2. chaque étape suivie de son annotation mot-clé / origine / confiance ; aucun terme technique dans l'étape
  3. aucun secret ni marqueur <MOT_DE_PASSE_n> ; confiance basse => question sur l'étape
  4. questions : extrait d'étape trouvé une seule fois, catégorie connue, question + proposition
  5. mot-clé présent dans resources/keywords/*.resource (sinon « NOUVEAU: »), avec autant de valeurs
     "entre guillemets" que d'arguments attendus
  6. traçabilité : si tests/<id>_*.robot existe, chaque mot-clé y est appelé, dans l'ordre du .feature
  7. statut : question bloquante sans réponse => brouillon ; tag « brouillon » du .robot <=> statut != actif

Génère toujours, pour chaque projet contrôlé, à partir de TOUS ses scénarios :
  projets/<p>/reports/validation_1.md (questions) et validation_2.md (scénario relu par l'auteur)

Usage : python tools/valider_features.py [projet | projets/<p>/features/X.feature ...]
        (sans argument : tous les projets)
"""
from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from gherkin.errors import ParserError
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

sys.path.insert(0, str(Path(__file__).resolve().parent))
import projets as P  # noqa: E402

ROOT = P.ROOT
ID_RE = re.compile(r"[A-Z][A-Z0-9]*-\d+")   # identifiant du scénario dans le Word (SC-001, TC-12…)
SECRET_RE = re.compile(r"(?i)(<(MOT_DE_PASSE|IDENTIFIANT|JETON)_\d+>|\bmdp\b\s*[:=]|password\s*[:=]"
                       r"|[\w.+-]+@[\w-]+\.[a-z]{2,})")
# Termes techniques interdits dans le texte d'une étape (ils vont dans l'annotation ou les localisateurs)
TECHNIQUE_RE = re.compile(r"(?i)(://|\$\{|css=|xpath|//\w|#[a-z][\w-]*\b|\[[\w-]+=|\bselector\b|\bsélecteur\b"
                          r"|\bdata-testid\b|\baria-label\b|\bclass(e)?=)")
STATUTS = ["brouillon", "a_valider", "valide", "actif"]
NIVEAUX_AUTO = {"total", "partiel", "non"}
CONFIANCES = {"haute", "moyenne", "basse"}
ORIGINE_RE = re.compile(r"^(texte|tableau|legende|deduit|image_\d{2})$")
CATEGORIES = {"attendu_manquant", "action_vague", "donnee_manquante", "contradiction_texte_image",
              "non_deterministe", "etapes_fusionnees", "dependance", "technique", "securite"}
QUESTION_RE = re.compile(r"^#\s*(Q\d+)\s*\|\s*(?:«\s*(.+?)\s*»|(-))\s*\|\s*(\w+)\s*\|\s*(bloquant|non bloquant)\s*$",
                         re.IGNORECASE)
ANCIEN_QUESTION_RE = re.compile(r"^#\s*Q\d+\s*\|\s*[ée]tape\s*\d+", re.IGNORECASE)
CHAMP_QUESTION_RE = re.compile(r"^#\s+(question|proposition|r[ée]ponse)\s*:\s*(.*)$", re.IGNORECASE)
VALEUR_RE = re.compile(r'"[^"]*"')


@dataclass
class Etape:
    n: int
    bloc: str          # « Contexte » ou nom du scénario
    texte: str         # mot-clé Gherkin + texte, ex. « Quand il recherche "lofi" »
    phrase: str        # texte sans le mot-clé Gherkin
    ligne: int
    mot_cle: str = ""
    origine: list[str] = field(default_factory=list)
    confiance: str = ""


@dataclass
class Scenario:
    chemin: Path
    id: str = "?"
    titre: str = ""
    persona: str = ""
    statut: str = ""
    auto: str = ""
    raison_auto: str = ""
    meta: dict[str, str] = field(default_factory=dict)
    etapes: list[Etape] = field(default_factory=list)
    nettoyage: list[str] = field(default_factory=list)
    questions: list[dict] = field(default_factory=list)


@dataclass
class MotCle:
    obligatoires: int = 0
    total: int = 0
    persona: bool = False   # argument ${persona} : fourni par le tag @persona, pas par l'étape


# --------------------------------------------------------------------------- utilitaires
def normalize(name: str) -> str:
    """Robot ignore casse, espaces et underscores."""
    return re.sub(r"[\s_]+", "", name).lower()


def cle(texte: str) -> str:
    """« Mot-Clé » → « motcle » (clés d'annotation tolérantes aux accents)."""
    sans_accent = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", sans_accent.lower())


def plier(texte: str) -> str:
    """Comparaison d'extraits : casse, espaces et apostrophes typographiques ignorés."""
    return re.sub(r"\s+", " ", texte.replace("’", "'")).strip().casefold()


def nom_mot_cle(mot_cle: str) -> str:
    return mot_cle.split(":", 1)[1].strip() if mot_cle.startswith("NOUVEAU:") else mot_cle


def keyword_catalog(projet: Path) -> dict[str, MotCle]:
    """Mots-clés de commun/*.resource et projets/<p>/resources/*.resource, avec leurs arguments."""
    catalogue: dict[str, MotCle] = {}
    for res in [*P.COMMUN.rglob("*.resource"), *(projet / "resources").rglob("*.resource")]:
        in_kw, courant, dans_args = False, None, False
        for line in res.read_text(encoding="utf-8").splitlines():
            if line.startswith("***"):
                in_kw = "keyword" in line.lower()
                continue
            if not in_kw or not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line[0].isspace():
                courant, dans_args = catalogue.setdefault(normalize(line.strip()), MotCle()), False
                continue
            cellules = [c for c in re.split(r"\s{2,}|\t", line.strip()) if c]
            if cellules[0].lower() == "[arguments]":
                dans_args, cellules = True, cellules[1:]
            elif cellules[0] == "..." and dans_args:
                cellules = cellules[1:]
            else:
                dans_args = False
                continue
            for arg in cellules:
                courant.total += 1
                courant.obligatoires += "=" not in arg
                courant.persona |= arg.split("=")[0].strip().lower() == "${persona}"
    return catalogue


def annotation(texte: str) -> dict[str, str]:
    """« # mot-clé: X | origine: a, b | confiance: haute » → {motcle: X, origine: …, confiance: …}."""
    champs = {}
    for part in texte.strip().lstrip("#").split("|"):
        k, sep, v = part.partition(":")
        if sep:
            champs[cle(k)] = v.strip()
    return champs


def tags_robot(code: str) -> set[str]:
    """Tags de « Test Tags » (avec ses lignes de suite « ... »)."""
    tags, dans = set(), False
    for line in code.splitlines():
        cellules = [c for c in re.split(r"\s{2,}|\t", line.strip()) if c]
        if not cellules:
            continue
        if cellules[0].lower() in {"test tags", "force tags"}:
            dans, cellules = True, cellules[1:]
        elif cellules[0] == "..." and dans:
            cellules = cellules[1:]
        else:
            dans = False
            continue
        tags.update(c.lower() for c in cellules)
    return tags


# --------------------------------------------------------------------------- lecture
def lire(chemin: Path) -> tuple[Scenario, list[str]]:
    sc, err = Scenario(chemin), []
    texte = chemin.read_text(encoding="utf-8")
    try:
        doc = Parser().parse(TokenScanner(texte))
    except ParserError as exc:
        return sc, [f"Gherkin invalide : {exc}"]
    feat = doc.get("feature")
    if not feat:
        return sc, ["aucune « Fonctionnalité: » dans le fichier"]
    if feat.get("language") != "fr":
        err.append("ajouter « # language: fr » en première ligne")

    # --- en-tête : tags et description « Clé: valeur »
    sc.titre = feat.get("name", "")
    for tag in (t["name"].lstrip("@") for t in feat.get("tags", [])):
        if ID_RE.fullmatch(tag):
            sc.id = tag
        elif ":" in tag:
            k, v = tag.split(":", 1)
            if k in {"persona", "statut", "auto"}:
                setattr(sc, k, v)
    for line in (feat.get("description") or "").splitlines():
        k, sep, v = line.strip().partition(":")
        if sep:
            sc.meta[cle(k)] = v.strip()
    sc.raison_auto = sc.meta.get("raisonauto", "")
    if sc.id == "?":
        err.append("tag d'identifiant manquant (@SC-001 : celui du Word, sinon le prochain numéro libre)")
    elif not chemin.name.startswith(sc.id + "_"):
        err.append(f"le nom du fichier doit commencer par « {sc.id}_ »")
    if not re.fullmatch(r"[a-z_]+", sc.persona):
        err.append("tag @persona:<nom_en_minuscules> manquant")
    if sc.statut not in STATUTS:
        err.append(f"tag @statut: attendu parmi {STATUTS}")
    if sc.auto not in NIVEAUX_AUTO:
        err.append(f"tag @auto: attendu parmi {sorted(NIVEAUX_AUTO)}")
    if "source" not in sc.meta:
        err.append("ligne « Source: <fichier.docx> § <section> » manquante sous la Fonctionnalité")

    # --- étapes numérotées dans l'ordre du fichier, avec leur annotation
    commentaires = sorted(doc.get("comments", []), key=lambda c: c["location"]["line"])
    blocs = []
    for child in feat.get("children", []):
        for genre in ("background", "scenario"):
            if genre in child:
                nom = "Contexte" if genre == "background" else child[genre].get("name", "")
                blocs.append((nom, child[genre]))
        if "rule" in child:
            err.append("« Règle: » non supportée : un fichier = un scénario du Word")
    if sum(1 for child in feat.get("children", []) if "scenario" in child) != 1:
        err.append("exactement un « Scénario: » (ou « Plan du scénario: ») attendu par fichier")
    lignes_etapes = [s["location"]["line"] for _, b in blocs for s in b.get("steps", [])]
    lignes_etapes.append(10**9)
    n = 0
    for nom, bloc in blocs:
        for step in bloc.get("steps", []):
            n += 1
            ligne = step["location"]["line"]
            fin = next(x for x in lignes_etapes if x > ligne)
            et = Etape(n, nom, f"{step['keyword'].strip()} {step['text']}", step["text"], ligne)
            for c in commentaires:
                if ligne < c["location"]["line"] < fin and "motcle" in annotation(c["text"]):
                    a = annotation(c["text"])
                    et.mot_cle, et.confiance = a.get("motcle", ""), a.get("confiance", "")
                    et.origine = [o.strip() for o in a.get("origine", "").split(",") if o.strip()]
                    break
            if not et.mot_cle:
                err.append(f"étape {n} (ligne {ligne}) : annotation « # mot-clé: … | origine: … | confiance: … » manquante")
            else:
                if et.confiance not in CONFIANCES:
                    err.append(f"étape {n} : confiance « {et.confiance} » ∉ {sorted(CONFIANCES)}")
                mauvaises = [o for o in et.origine if not ORIGINE_RE.match(o)]
                if not et.origine or mauvaises:
                    err.append(f"étape {n} : origine invalide {mauvaises or '(vide)'} "
                               "(texte, tableau, legende, deduit, image_NN)")
            technique = TECHNIQUE_RE.search(VALEUR_RE.sub("", step["text"]))
            if technique:
                err.append(f"étape {n} : terme technique « {technique[0]} » dans la phrase métier "
                           "(le mettre dans l'annotation ou les localisateurs)")
            sc.etapes.append(et)
    for c in commentaires:
        k, sep, v = c["text"].strip().lstrip("#").partition(":")
        if sep and cle(k) == "nettoyage":
            sc.nettoyage.append(v.strip())

    # --- questions (bloc de commentaires en fin de fichier)
    courant, derniere_ligne, dernier_champ = None, -1, None
    for c in commentaires:
        t, ligne = c["text"].strip(), c["location"]["line"]
        m = QUESTION_RE.match(t)
        if m:
            courant = {"id": m[1], "ancre": m[2] or "", "etape": "-", "categorie": m[4].lower(),
                       "bloquant": m[5].lower() == "bloquant", "question": "", "proposition": "", "reponse": "",
                       "ligne": ligne}
            sc.questions.append(courant)
            dernier_champ = None
        elif ANCIEN_QUESTION_RE.match(t):
            err.append(f"ligne {ligne} : ancien format « étape N » ; écrire « # Qn | « extrait de l'étape » | … »")
            courant = None
        elif courant and ligne == derniere_ligne + 1:
            mc = CHAMP_QUESTION_RE.match(t)
            if mc:
                dernier_champ = cle(mc[1])
                courant[dernier_champ] = mc[2].strip()
            elif dernier_champ and t.lstrip("#").strip():
                courant[dernier_champ] += " " + t.lstrip("#").strip()
            else:
                courant = None
        else:
            courant = None
        derniere_ligne = ligne
    ids_vus = set()
    for q in sc.questions:
        if q["id"] in ids_vus:
            err.append(f"{q['id']} en double")
        ids_vus.add(q["id"])
        if q["ancre"]:
            trouvees = [e for e in sc.etapes if plier(q["ancre"]) in plier(e.phrase)]
            if len(trouvees) == 1:
                q["etape"] = str(trouvees[0].n)
            else:
                err.append(f"{q['id']} : l'extrait « {q['ancre']} » correspond à {len(trouvees)} étapes "
                           "(il en faut exactement une : allonger ou corriger l'extrait)")
        if q["categorie"] not in CATEGORIES:
            err.append(f"{q['id']} : catégorie « {q['categorie']} » ∉ {sorted(CATEGORIES)}")
        if not q["question"] or not q["proposition"]:
            err.append(f"{q['id']} : lignes « question: » et « proposition: » obligatoires")
    for et in sc.etapes:
        if et.confiance == "basse" and not any(q["etape"] == str(et.n) for q in sc.questions):
            err.append(f"étape {et.n} : confiance basse sans question associée")

    if SECRET_RE.search(texte):
        err.append("secret ou identifiant détecté — utiliser un persona (voir docs/credentials.md)")
    return sc, err


def controler(sc: Scenario, catalog: dict[str, MotCle]) -> list[str]:
    err = []
    mots = [(f"étape {e.n}", e.mot_cle) for e in sc.etapes if e.mot_cle] + [("nettoyage", m) for m in sc.nettoyage]
    for ou, kw in mots:
        if kw.startswith("NOUVEAU:"):
            if normalize(nom_mot_cle(kw)) in catalog:
                err.append(f"{ou} : « {nom_mot_cle(kw)} » existe maintenant, retirer le préfixe NOUVEAU:")
        elif normalize(kw) not in catalog:
            err.append(f"{ou} : mot-clé inconnu « {kw} » (l'ajouter au catalogue ou préfixer NOUVEAU:)")

    # --- nombre de valeurs "entre guillemets" = arguments du mot-clé
    if sc.auto != "non":
        for e in sc.etapes:
            mk = catalog.get(normalize(e.mot_cle))
            if not mk:
                continue
            nb = len(VALEUR_RE.findall(e.phrase))
            fourni = nb + (1 if mk.persona else 0)
            if not mk.obligatoires <= fourni <= mk.total:
                attendu = (f"{mk.obligatoires}" if mk.obligatoires == mk.total
                           else f"{mk.obligatoires} à {mk.total}")
                err.append(f"étape {e.n} : {nb} valeur(s) entre guillemets pour « {e.mot_cle} », "
                           f"qui attend {attendu} argument(s)" + (" dont ${persona} (tag)" if mk.persona else ""))

    # --- traçabilité et ordre .feature ↔ .robot
    robots = sorted((sc.chemin.parent.parent / "tests").glob(f"{sc.id}_*.robot"))
    if robots:
        brut = robots[0].read_text(encoding="utf-8")
        code = normalize(brut)
        for ou, kw in mots:
            if normalize(nom_mot_cle(kw)) not in code:
                err.append(f"traçabilité : {ou} « {nom_mot_cle(kw)} » absent de {robots[0].name}")
        corps = normalize(brut.split("*** Test Cases ***", 1)[-1])
        position = 0
        for e in sc.etapes:
            trouve = corps.find(normalize(nom_mot_cle(e.mot_cle)), position)
            if trouve < 0 and normalize(nom_mot_cle(e.mot_cle)) in corps:
                err.append(f"ordre : étape {e.n} « {nom_mot_cle(e.mot_cle)} » appelée trop tôt dans {robots[0].name}")
                break
            position = max(position, trouve)
        brouillon = "brouillon" in tags_robot(brut)
        if sc.statut == "actif" and brouillon:
            err.append(f"statut actif mais {robots[0].name} porte encore le tag « brouillon »")
        if sc.statut != "actif" and not brouillon:
            err.append(f"{robots[0].name} sans tag « brouillon » : passer le .feature en @statut:actif (après V4)")
        if sc.statut in {"brouillon", "a_valider"}:
            err.append(f"{robots[0].name} existe alors que le scénario n'est pas validé (statut {sc.statut})")
    elif sc.statut == "actif":
        err.append("statut actif sans fichier tests/<id>_*.robot")

    if sc.statut != "brouillon":
        for q in sc.questions:
            if q["bloquant"] and not q["reponse"]:
                err.append(f"{q['id']} bloquante sans réponse alors que statut = {sc.statut}")
    return err


# --------------------------------------------------------------------------- fiches
def _question_md(q: dict) -> list[str]:
    ou = "tout le scénario" if q["etape"] == "-" else f"étape {q['etape']}"
    return [f"- **{q['id']}** _({ou}, {q['categorie']})_ — {q['question']}",
            f"  - Proposition par défaut : {q['proposition']}", "  - Réponse : "]


def fiche_questions(scenarios: list[Scenario]) -> str:
    out = ["# Validation 1 — Ambiguïtés à trancher", "",
           "Seules les questions **bloquantes** demandent une réponse. Les autres sont repliées : sans objection, "
           "leur proposition par défaut est appliquée (`/valider tout`).",
           "Répondre ici sous chaque question, dans la fiche Word (`w2r fiche-word`), ou directement dans le chat.",
           "Décisions déjà prises (non redemandées) : `conventions.md` du projet et `commun/conventions.md`.", ""]
    for sc in scenarios:
        ouvertes = [q for q in sc.questions if not q["reponse"]]
        bloquantes = [q for q in ouvertes if q["bloquant"]]
        autres = [q for q in ouvertes if not q["bloquant"]]
        out += [f"## {sc.id} — {sc.titre}",
                f"Persona : `{sc.persona}` · Automatisable : **{sc.auto}** · Statut : `{sc.statut}` · "
                f"Questions ouvertes : {len(ouvertes)} (dont {len(bloquantes)} bloquante"
                f"{'s' if len(bloquantes) > 1 else ''})", ""]
        if sc.raison_auto:
            out += [f"> {sc.raison_auto}", ""]
        if bloquantes:
            out.append("### 🔴 À trancher")
            for q in bloquantes:
                out += _question_md(q)
            out.append("")
        if autres:
            out += [f"<details><summary>🟡 {len(autres)} question(s) non bloquante(s) — proposition appliquée "
                    "par défaut</summary>", ""]
            for q in autres:
                out += _question_md(q)
            out += ["", "</details>", ""]
        if not ouvertes:
            out += ["✅ Aucune question ouverte.", ""]
    return "\n".join(out) + "\n"


def fiche_intention(scenarios: list[Scenario]) -> str:
    out = ["# Validation 2 — Est-ce bien ce que vous vouliez tester ?", "",
           "À faire relire par l'auteur du Word (ou via la fiche Word : `w2r fiche-word`). "
           "Si c'est correct, cocher « Conforme » puis lancer `/valider`.", ""]
    for sc in scenarios:
        out += [f"## {sc.id} — {sc.titre}"]
        if sc.meta.get("objectif"):
            out.append(f"_{sc.meta['objectif']}_  ")
        out += [f"Source : {sc.meta.get('source', '?')} · Persona : `{sc.persona}` · Statut : `{sc.statut}`", ""]
        bloc = None
        for e in sc.etapes:
            if e.bloc != bloc:
                bloc = e.bloc
                out.append(f"**{'Préconditions' if bloc == 'Contexte' else 'Scénario'}**")
            out.append(f"{e.n}. {e.texte}{' ⚠️' if e.confiance == 'basse' else ''}")
        if sc.nettoyage:
            out += ["", "**Nettoyage** : " + " ; ".join(nom_mot_cle(m) for m in sc.nettoyage)]
        out += ["", "- [ ] Conforme à l'intention    - [ ] À corriger : …", ""]
    return "\n".join(out) + "\n"


def features(projet: Path) -> list[Path]:
    return sorted((projet / "features").glob("*.feature"))


def charger_tous(projet: Path) -> list[tuple[Scenario, list[str]]]:
    """Tous les .feature d'un projet, lus et contrôlés (utilisé aussi par fiche_word.py)."""
    catalog = keyword_catalog(projet)
    resultat = []
    for f in features(projet):
        sc, err = lire(f)
        resultat.append((sc, err + (controler(sc, catalog) if sc.etapes else [])))
    return resultat


def valider_projet(projet: Path, a_controler: set[Path] | None) -> int:
    """Contrôle les fichiers demandés (tous si None), régénère les fiches du projet ; renvoie le nb d'échecs."""
    catalog = keyword_catalog(projet)
    scenarios, echecs, ids = [], 0, {}
    print(f"## Projet {projet.name}")
    for f in features(projet):
        sc, err = lire(f)
        err += controler(sc, catalog) if sc.etapes else []
        if sc.id in ids:
            err.append(f"identifiant {sc.id} déjà utilisé par {ids[sc.id]}")
        ids[sc.id] = f.name
        if a_controler is None or f.resolve() in a_controler:
            if err:
                echecs += 1
                print(f"✗ {f.name}")
                print("\n".join(f"    - {e}" for e in err))
            else:
                print(f"✓ {f.name}")
        if sc.etapes:
            scenarios.append(sc)

    if scenarios:
        print("\n| Scénario | Statut | Auto | Questions ouvertes (bloquantes) | .robot |")
        print("|---|---|---|---|---|")
        for sc in scenarios:
            ouv = [q for q in sc.questions if not q["reponse"]]
            robots = sorted((projet / "tests").glob(f"{sc.id}_*.robot"))
            robot = "non"
            if robots:
                robot = "brouillon" if "brouillon" in tags_robot(robots[0].read_text(encoding="utf-8")) else "actif"
            print(f"| {sc.id} {sc.titre} | {sc.statut} | {sc.auto} | {len(ouv)} "
                  f"({sum(q['bloquant'] for q in ouv)}) | {robot} |")
    rapports = projet / "reports"
    rapports.mkdir(exist_ok=True)
    (rapports / "validation_1.md").write_text(fiche_questions(scenarios), encoding="utf-8")
    (rapports / "validation_2.md").write_text(fiche_intention(scenarios), encoding="utf-8")
    print(f"\n→ {P.relatif(rapports)}/validation_1.md + validation_2.md ({len(scenarios)} scénarios, "
          f"{len(catalog)} mots-clés au catalogue)\n")
    return echecs


# --------------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    for _flux in (sys.stdout, sys.stderr):
        _flux.reconfigure(encoding="utf-8")
    cibles: dict[Path, set[Path] | None] = {}
    for arg in argv:
        if arg in P.noms():
            cibles[P.resoudre(arg)] = None
            continue
        projet = P.depuis_chemin(arg)
        if not projet:
            print(f"✗ {arg} : ni un projet ({', '.join(P.noms())}), ni un fichier de projets/<projet>/features/")
            return 2
        if cibles.get(projet, set()) is not None:
            cibles.setdefault(projet, set()).add(Path(arg).resolve())
    if not argv:
        cibles = {p: None for p in P.lister()}
    if not cibles:
        print("Aucun projet : w2r nouveau-projet <nom>")
        return 0
    return 1 if sum(valider_projet(p, fichiers) for p, fichiers in cibles.items()) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
