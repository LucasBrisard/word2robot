"""Projets : un dossier de projets/ par application testée, reconnu à son fichier projet.yaml."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJETS = ROOT / "projets"
COMMUN = ROOT / "commun"


def lister() -> list[Path]:
    return sorted(p for p in PROJETS.iterdir() if (p / "projet.yaml").exists()) if PROJETS.exists() else []


def noms() -> list[str]:
    return [p.name for p in lister()]


def resoudre(nom: str | None = None) -> Path:
    """Projet nommé, ou le seul projet existant ; sinon erreur explicite."""
    if nom:
        p = PROJETS / nom
        if (p / "projet.yaml").exists():
            return p
        raise SystemExit(f"Projet inconnu « {nom} ». Projets : {', '.join(noms()) or 'aucun'} "
                         "(w2r nouveau-projet <nom> pour en créer un).")
    projets = lister()
    if len(projets) == 1:
        return projets[0]
    raise SystemExit(f"Préciser le projet : {', '.join(noms()) or 'aucun projet (w2r nouveau-projet <nom>)'}.")


def depuis_chemin(chemin: str | Path) -> Path | None:
    """projets/<nom>/… → dossier du projet (None si le chemin n'est dans aucun projet)."""
    p = Path(chemin).resolve()
    for projet in lister():
        if p == projet or projet in p.parents:
            return projet
    return None


def separer(args: list[str]) -> tuple[Path, list[str]]:
    """« [projet] reste… » : le premier argument est le projet s'il en porte le nom."""
    if args and args[0] in noms():
        return resoudre(args[0]), args[1:]
    return resoudre(None), args


def relatif(chemin: Path) -> str:
    return chemin.relative_to(ROOT).as_posix()
