#!/usr/bin/env python3
"""Contrôle de stabilité avant la V4 : exécute N fois les mêmes tests et compte les réussites.

Un test n'est proposé à la V4 (retrait du tag « brouillon ») que s'il passe N fois sur N : les publicités,
les données de production et les temps de chargement varient d'une exécution à l'autre.

Usage : python tools/stabilite.py [projet] [N] [arguments robot]
  projet : facultatif s'il n'y en a qu'un ; N par défaut : 3
  arguments par défaut : --include brouillon projets/<p>/tests
  Résultats : projets/<p>/reports/run/stabilite/passage_<i>/ (log.html de chaque passage)
Code retour 0 si chaque test est passé N fois sur N, 1 sinon.
"""
from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from robot.api import ExecutionResult

sys.path.insert(0, str(Path(__file__).resolve().parent))
import projets as P  # noqa: E402


def main(argv: list[str]) -> int:
    for _flux in (sys.stdout, sys.stderr):
        _flux.reconfigure(encoding="utf-8")
    projet, argv = P.separer(argv)
    n = int(argv[0]) if argv and argv[0].isdigit() else 3
    args = (argv[1:] if argv and argv[0].isdigit() else argv) or ["--include", "brouillon",
                                                                    P.relatif(projet / "tests")]
    sortie_racine = projet / "reports" / "run" / "stabilite"
    resultats: dict[str, list[str]] = defaultdict(list)
    messages: dict[str, list[str]] = defaultdict(list)
    for i in range(1, n + 1):
        dossier = sortie_racine / f"passage_{i}"
        print(f"— passage {i}/{n}", flush=True)
        subprocess.run(["robot", "--outputdir", str(dossier), "--console", "dotted", *args], cwd=P.ROOT)
        sortie = dossier / "output.xml"
        if not sortie.exists():
            print("  aucun résultat (aucun test sélectionné ?)")
            return 1
        for test in ExecutionResult(str(sortie)).suite.all_tests:
            resultats[test.name].append(test.status)
            if test.status == "FAIL":
                messages[test.name].append(f"passage {i} : {test.message.splitlines()[0][:150]}")

    if not resultats:
        print("Aucun test exécuté.")
        return 1
    stable = True
    print("\n| Test | Réussites | Statuts | Verdict |\n|---|---|---|---|")
    for nom, statuts in resultats.items():
        ok = statuts.count("PASS")
        verdict = "stable" if ok == n else ("SKIP" if set(statuts) == {"SKIP"} else "INSTABLE")
        stable &= verdict != "INSTABLE"
        print(f"| {nom} | {ok}/{n} | {' '.join(statuts)} | {verdict} |")
    for nom, msgs in messages.items():
        print(f"\n{nom} :")
        print("\n".join(f"  - {m}" for m in msgs))
    print(f"\n→ logs : {P.relatif(sortie_racine)}/passage_1..{n}/log.html")
    return 0 if stable else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
