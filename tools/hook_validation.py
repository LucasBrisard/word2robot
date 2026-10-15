#!/usr/bin/env python3
"""Hook Claude Code (PostToolUse) : valide automatiquement chaque fichier modifié.

- features/*.feature     → tools/valider_features.py sur ce fichier
- *.robot / *.resource   → robocop check + recherche de secrets en dur
Code retour 2 = l'erreur est renvoyée à Claude, qui doit corriger avant de continuer.

Lancé dans le conteneur par « w2r hook » : le chemin reçu est celui du poste, traduit grâce à W2R_HOTE.
Chaque appel est tracé dans .w2r/hook.log (preuve que le hook se déclenche, et son résultat).
GitHub Copilot n'a pas ce mécanisme : ses procédures lancent « w2r valider » et « w2r lint » à la place.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath

for _flux in (sys.stdout, sys.stderr):
    _flux.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / ".w2r" / "hook.log"
SECRET = re.compile(r"(?i)(password|mot_de_passe|mdp|token|secret)\s*[:=]\s*['\"]?[^\s'\"$%{]{4,}")


def chemin_local(brut: str) -> Path:
    """C:\\…\\word2robot\\features\\x.feature (poste) → /work/features/x.feature (conteneur)."""
    if Path(brut).exists():
        return Path(brut)
    hote = os.environ.get("W2R_HOTE") or os.environ.get("CLAUDE_PROJECT_DIR", "")
    for pure in (PureWindowsPath, PurePosixPath):
        try:
            return ROOT / pure(brut).relative_to(pure(hote))
        except ValueError:
            continue
    return Path(brut)


def tracer(fichier: str, resultat: str) -> None:
    JOURNAL.parent.mkdir(exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {resultat:<10} {fichier}\n")


def main() -> int:
    data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")  # tolère un BOM en tête
    brut = data.get("tool_input", {}).get("file_path", "")
    path = chemin_local(brut) if brut else None
    if not path or not path.exists():
        tracer(brut or "?", "ignoré")
        return 0
    rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)

    errors = []
    if path.suffix == ".feature" and path.parent.name == "features":  # projets/<p>/features/
        r = subprocess.run([sys.executable, str(ROOT / "tools/valider_features.py"), str(path)],
                           capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode:
            errors.append(r.stdout + r.stderr)
    elif path.suffix in {".robot", ".resource"}:
        r = subprocess.run(["robocop", "check", str(path)], capture_output=True, text=True, encoding="utf-8",
                           cwd=ROOT)
        if "No issues found" not in r.stdout:
            errors.append(r.stdout[-3000:])
        if SECRET.search(path.read_text(encoding="utf-8")):
            errors.append("Secret en dur détecté : utiliser un persona et Fill Secret (voir docs/credentials.md).")
    else:
        tracer(rel, "non suivi")
        return 0

    tracer(rel, "ERREUR" if errors else "ok")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
