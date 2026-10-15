#!/usr/bin/env python3
"""Commandes word2robot, exécutées DANS le conteneur (appelées par w2r.ps1 / w2r).
[projet] = nom d'un dossier de projets/ ; facultatif s'il n'y a qu'un projet.

  nouveau-projet <nom>         crée projets/<nom>/ à partir de modele/
  extraire <docx>              étape 1 : projets/<p>/scenarios_word/X.docx → projets/<p>/extracted/X/
  valider [projet|feature…]    contrôle des .feature + fiches V1/V2 (sans argument : tous les projets)
  fiche-word [projet] [docx]   fiche de validation Word pour l'auteur (projets/<p>/reports/)
  import-word <fiche.docx>     relit les réponses d'une fiche Word remplie et les reporte dans les .feature
  lint                         robocop check + format --check (commun/ et projets/)
  format                       robocop format
  dryrun [projet]              robot --dryrun strict (sans argument : tous les projets)
  test [projet] [args robot]   exécution réelle → projets/<p>/reports/run
  stabilite [projet] [n]       n passages (3) des tests « brouillon » → projets/<p>/reports/run/stabilite
  lock                         fige les versions Python installées dans requirements.lock
  hook                         hook Claude Code (fichier modifié lu sur l'entrée standard)
  mcp-playwright | mcp-robot   serveurs MCP Playwright et Robot Framework (rf-mcp)

Toute autre commande est exécutée telle quelle (ex. « w2r robot --version »).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

import projets as P


def _tests(projets: list) -> list[str]:
    return [P.relatif(p / "tests") for p in projets if any((p / "tests").glob("*.robot"))]


def nouveau_projet(args: list[str]) -> int:
    if not args or not re.fullmatch(r"[a-z][a-z0-9_-]*", args[0]):
        print("Usage : w2r nouveau-projet <nom>  (minuscules, chiffres, - ou _ ; ex. facturation)")
        return 2
    cible = P.PROJETS / args[0]
    if cible.exists():
        print(f"✗ {P.relatif(cible)} existe déjà")
        return 1
    shutil.copytree(P.ROOT / "modele", cible)
    for f in cible.rglob("*"):
        if f.is_file() and f.suffix in {".yaml", ".md", ".resource"}:
            f.write_text(f.read_text(encoding="utf-8").replace("{{PROJET}}", args[0]), encoding="utf-8")
    print(f"✓ {P.relatif(cible)} créé. Compléter projet.yaml (URL_ACCUEIL), puis copier les Word dans "
          f"{P.relatif(cible / 'scenarios_word')}/ et lancer /traduire.")
    return 0


def commande(nom: str, args: list[str]) -> list[str] | int:
    if nom == "nouveau-projet":
        return nouveau_projet(args)
    if nom == "extraire":
        if not args:
            print("Usage : w2r extraire projets/<projet>/scenarios_word/<fichier>.docx")
            return 2
        projet = P.depuis_chemin(args[0])
        if not projet:
            print(f"✗ {args[0]} n'est dans aucun projet : le copier dans projets/<projet>/scenarios_word/")
            return 2
        return ["python", "tools/extract_docx.py", *args, "--out", P.relatif(projet / "extracted")]
    if nom == "valider":
        return ["python", "tools/valider_features.py", *args]
    if nom == "fiche-word":
        return ["python", "tools/fiche_word.py", "export", *args]
    if nom == "import-word":
        return ["python", "tools/fiche_word.py", "import", *args]
    if nom == "format":
        return ["robocop", "format", "commun", "projets", *args]
    if nom == "lint":
        r = subprocess.run(["robocop", "check", "commun", "projets"])
        return r.returncode or subprocess.run(["robocop", "format", "--check", "commun", "projets"]).returncode
    if nom == "dryrun":
        dossiers = _tests([P.resoudre(args[0])] if args else P.lister())
        if not dossiers:
            print("Aucun test .robot à vérifier.")
            return 0
        return ["robot", "--dryrun", "--exitonerror", "--output", "NONE", "--log", "NONE", "--report", "NONE",
                *dossiers]
    if nom == "test":
        projet, reste = P.separer(args)
        return ["robot", "--outputdir", P.relatif(projet / "reports" / "run"), *(reste or _tests([projet]))]
    if nom == "stabilite":
        return ["python", "tools/stabilite.py", *args]
    if nom == "lock":
        gele = subprocess.run([sys.executable, "-m", "pip", "freeze", "--exclude-editable"],
                              capture_output=True, text=True, check=True).stdout
        (P.ROOT / "requirements.lock").write_text(
            "# Généré par « w2r lock » : versions exactes de l'image. Ne pas éditer à la main.\n" + gele,
            encoding="utf-8")
        print(f"requirements.lock : {len(gele.splitlines())} paquets")
        return 0
    if nom == "hook":
        return ["python", "tools/hook_validation.py"]
    if nom == "mcp-playwright":
        return ["playwright-mcp", "--headless", "--browser", "chromium", "--no-sandbox", "--isolated",
                "--viewport-size", "1366,900", "--output-dir", "/work/.w2r/mcp", *args]
    if nom == "mcp-robot":
        return ["robotmcp", *args]
    return [nom, *args]


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help", "aide"}:
        print(__doc__)
        return 0
    os.chdir(P.ROOT)
    resultat = commande(argv[0], argv[1:])
    if isinstance(resultat, int):
        return resultat
    os.execvp(resultat[0], resultat)  # remplace le processus : entrée/sortie transmises telles quelles (MCP)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
