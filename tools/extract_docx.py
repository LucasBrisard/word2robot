#!/usr/bin/env python3
"""Étape 1 du pipeline : extraction d'un cahier de recette Word.

Produit, dans <out>/<nom_du_doc>/ (w2r : projets/<projet>/extracted/) :
  - extraction.json : blocs dans l'ordre du document (titres, paragraphes, tableaux, images)
                      avec l'ancrage de chaque image (section + légende la plus proche)
  - extraction.md   : la même chose lisible par un humain ou par l'IA
  - images/         : captures extraites, zones sensibles masquées si l'OCR est disponible
  - secrets_report.md : ce qui a été masqué (type + emplacement, JAMAIS la valeur)

Aucun secret ne sort de cette étape : le texte est expurgé avant d'être écrit.

Usage : w2r extraire projets/<projet>/scenarios_word/MonFichier.docx
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
for _flux in (sys.stdout, sys.stderr):
    _flux.reconfigure(encoding="utf-8")
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

try:  # OCR facultatif pour masquer les secrets visibles sur les captures
    import pytesseract
    from PIL import Image, ImageDraw
    OCR = True
except ImportError:  # pragma: no cover
    OCR = False

# --------------------------------------------------------------------------- secrets
SECRET_PATTERNS = [
    # "mdp : xxx", "mot de passe = xxx", "password: xxx"
    ("mot_de_passe", re.compile(r"(?i)\b(mdp|mot\s+de\s+passe|password|passwd|pwd)\b\s*[:=]?\s*(\S+)")),
    ("jeton", re.compile(r"(?i)\b(token|api[_-]?key|secret|bearer)\b\s*[:=]?\s*([A-Za-z0-9_\-\.]{12,})")),
    ("jeton", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b")),  # JWT
]
LOGIN_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")  # identifiant de compte (email)
SENSITIVE_OCR_WORDS = re.compile(r"(?i)^(mdp|password|mot|passe|token|@)")


class Redactor:
    def __init__(self) -> None:
        self.findings: list[dict] = []
        self._n = 0
        self.ocr_indisponible = False

    def _marker(self, kind: str, where: str) -> str:
        self._n += 1
        self.findings.append({"marqueur": f"<{kind.upper()}_{self._n}>", "type": kind, "emplacement": where})
        return f"<{kind.upper()}_{self._n}>"

    def text(self, value: str, where: str) -> str:
        for kind, pat in SECRET_PATTERNS:
            def repl(m: re.Match, kind=kind) -> str:
                if m.lastindex and m.lastindex >= 2:  # garder le libellé, masquer la valeur
                    return m.group(0)[: m.start(2) - m.start()] + self._marker(kind, where)
                return self._marker(kind, where)
            value = pat.sub(repl, value)
        # Un email à côté d'un mot de passe = identifiant de compte : on le masque aussi
        if any(f["emplacement"] == where and f["type"] == "mot_de_passe" for f in self.findings):
            value = LOGIN_PATTERN.sub(lambda m: self._marker("identifiant", where), value)
        return value

    def image(self, data: bytes, where: str) -> tuple[bytes, int]:
        """Masque en noir les mots OCR qui ressemblent à des secrets. Retourne (png, nb_zones)."""
        if not OCR:
            return data, 0
        img = Image.open(io.BytesIO(data)).convert("RGB")
        try:
            langs = pytesseract.get_languages()
            ocr = pytesseract.image_to_data(img, lang="fra+eng" if "fra" in langs else "eng",
                                            output_type=pytesseract.Output.DICT)
        except (pytesseract.TesseractNotFoundError, OSError):
            self.ocr_indisponible = True
            return data, 0
        draw, zones = ImageDraw.Draw(img), 0
        words = ocr["text"]
        for i, w in enumerate(words):
            w = (w or "").strip()
            if not w:
                continue
            prev = (words[i - 1] or "").strip() if i else ""
            if SENSITIVE_OCR_WORDS.match(w) or LOGIN_PATTERN.search(w) or re.match(r"(?i)mdp|password", prev):
                x, y, ww, hh = ocr["left"][i], ocr["top"][i], ocr["width"][i], ocr["height"][i]
                draw.rectangle([x - 2, y - 2, x + ww + 2, y + hh + 2], fill="black")
                zones += 1
        if zones:
            self._marker("zone_image", where)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue(), zones


# --------------------------------------------------------------------------- parcours
def iter_blocks(doc):
    """Parcourt le corps du document dans l'ordre réel (paragraphes ET tableaux)."""
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def paragraph_images(par: Paragraph, doc) -> list[bytes]:
    out = []
    for blip in par._element.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid and rid in doc.part.related_parts:
            out.append(doc.part.related_parts[rid].blob)
    return out


def extract(docx_path: Path, out_root: Path) -> Path:
    doc = Document(str(docx_path))
    out = out_root / docx_path.stem
    (out / "images").mkdir(parents=True, exist_ok=True)
    red = Redactor()
    blocks: list[dict] = []
    section = "(début)"
    img_n = 0

    for b in iter_blocks(doc):
        if isinstance(b, Table):
            rows = []
            for r_i, row in enumerate(b.rows):
                rows.append([red.text(c.text.strip(), f"{section} / tableau ligne {r_i}") for c in row.cells])
            blocks.append({"type": "tableau", "section": section, "lignes": rows})
            continue

        style = (b.style.name or "").lower() if b.style is not None else ""
        text = b.text.strip()
        for data in paragraph_images(b, doc):
            img_n += 1
            name = f"image_{img_n:02d}.png"
            clean, zones = red.image(data, f"{section} / {name}")
            (out / "images" / name).write_bytes(clean)
            blocks.append({"type": "image", "section": section, "fichier": f"images/{name}",
                           "zones_masquees": zones, "legende": None})
        if not text:
            continue
        text = red.text(text, section)
        if style.startswith("heading") or style == "title":
            if style != "title":
                section = text
            blocks.append({"type": "titre", "niveau": style, "texte": text})
        else:
            kind = "puce" if "list" in style or b._element.pPr is not None and b._element.pPr.numPr is not None else "paragraphe"
            blocks.append({"type": kind, "section": section, "texte": text})

    # Ancrage : une légende "Capture N ..." juste après une image lui est rattachée
    for i, blk in enumerate(blocks):
        if blk["type"] == "image" and i + 1 < len(blocks):
            nxt = blocks[i + 1]
            if nxt.get("texte", "").lower().startswith(("capture", "figure", "image")):
                blk["legende"] = nxt["texte"]

    ocr_actif = OCR and not red.ocr_indisponible
    if not ocr_actif:
        print("⚠ OCR indisponible (installer Tesseract) : les captures ne sont PAS expurgées, les vérifier à la main")
    result = {"source": docx_path.name, "nb_images": img_n, "ocr_actif": ocr_actif, "blocs": blocks}
    (out / "extraction.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "extraction.md").write_text(to_markdown(result), encoding="utf-8")
    (out / "secrets_report.md").write_text(secrets_report(docx_path.name, red.findings), encoding="utf-8")
    return out


def to_markdown(res: dict) -> str:
    lines = [f"# Extraction de {res['source']}", ""]
    for b in res["blocs"]:
        t = b["type"]
        if t == "titre":
            lines += ["", f"## {b['texte']}", ""]
        elif t == "paragraphe":
            lines += ["", b["texte"], ""]
        elif t == "puce":
            lines.append(f"- {b['texte']}")
        elif t == "tableau":
            head, *rows = b["lignes"]
            lines += ["", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
            lines += ["| " + " | ".join(c or "∅" for c in r) + " |" for r in rows]
            lines.append("")
        elif t == "image":
            leg = f" — légende : « {b['legende']} »" if b["legende"] else " — ⚠ sans légende"
            lines += ["", f"![{b['fichier']}]({b['fichier']}){leg}", ""]
    return "\n".join(lines) + "\n"


def secrets_report(source: str, findings: list[dict]) -> str:
    if not findings:
        return f"# Secrets – {source}\n\nAucun secret détecté.\n"
    lines = [f"# Secrets détectés – {source}", "",
             "Les valeurs ont été remplacées par des marqueurs et ne figurent nulle part dans les sorties.",
             "**Action requise** : si ces identifiants sont réels, les faire changer et retirer du Word.", "",
             "| Marqueur | Type | Emplacement |", "|---|---|---|"]
    lines += [f"| `{f['marqueur']}` | {f['type']} | {f['emplacement']} |" for f in findings]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=Path("extracted"))
    args = ap.parse_args()
    for d in args.docx:
        out = extract(d, args.out)
        print(f"✓ {d.name} → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
