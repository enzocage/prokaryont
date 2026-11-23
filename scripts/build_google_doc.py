"""Konvertiert organisches_unternehmen.md inkl. aller 50 Bilder in ein Google-Docs-kompatibles .docx."""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "organisches_unternehmen.md"
OUT_DOCX = ROOT / "docs" / "organisches_unternehmen_google_doc.docx"
OUT_HTML = ROOT / "docs" / "organisches_unternehmen_google_doc.html"


def _set_cell_bg(cell, hex_color: str) -> None:
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def _set_paragraph_shading(paragraph, hex_color: str, left_border_hex: str | None = None) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    pPr.append(shd)
    if left_border_hex:
        pBdr = OxmlElement("w:pBdr")
        left = OxmlElement("w:left")
        left.set(qn("w:val"), "single")
        left.set(qn("w:sz"), "24")
        left.set(qn("w:space"), "8")
        left.set(qn("w:color"), left_border_hex)
        pBdr.append(left)
        pPr.append(pBdr)


def _add_inline_formatted(paragraph, text: str, base_color: RGBColor | None = None) -> None:
    """Rendert **fett**, *kursiv* und `code` sauber in python-docx Runs."""
    token_re = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)")
    pos = 0
    for m in token_re.finditer(text):
        if m.start() > pos:
            r = paragraph.add_run(text[pos : m.start()])
            if base_color:
                r.font.color.rgb = base_color
        tok = m.group(0)
        if tok.startswith("**") and tok.endswith("**"):
            r = paragraph.add_run(tok[2:-2])
            r.bold = True
            if base_color:
                r.font.color.rgb = base_color
        elif tok.startswith("`") and tok.endswith("`"):
            r = paragraph.add_run(tok[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0x0E, 0x74, 0x90)
        elif tok.startswith("*") and tok.endswith("*"):
            r = paragraph.add_run(tok[1:-1])
            r.italic = True
            if base_color:
                r.font.color.rgb = base_color
        pos = m.end()
    if pos < len(text):
        r = paragraph.add_run(text[pos:])
        if base_color:
            r.font.color.rgb = base_color


def build_docx(md_path: Path = MD_PATH, out_docx: Path = OUT_DOCX) -> int:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # Deckblatt
    cover_title = doc.add_paragraph()
    cover_title.paragraph_format.space_before = Pt(36)
    cover_title.paragraph_format.space_after = Pt(8)
    r_title = cover_title.add_run("PROKARYONT")
    r_title.bold = True
    r_title.font.size = Pt(28)
    r_title.font.color.rgb = RGBColor(0x0B, 0x3B, 0x5B)

    cover_sub = doc.add_paragraph()
    cover_sub.paragraph_format.space_after = Pt(18)
    r_sub = cover_sub.add_run(
        "Das Organische Unternehmen — Vom Maschinen-Ingenieur zum Nutzpflanzen-Gärtner\n"
        "Vollständige kausale Systemerklärung mit 50 Illustrationen anhand des simulierten Prokaryonten"
    )
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(0x0F, 0x76, 0x6E)

    cover_box = doc.add_paragraph()
    cover_box.paragraph_format.space_before = Pt(8)
    cover_box.paragraph_format.space_after = Pt(16)
    _set_paragraph_shading(cover_box, "ECFEFF", "0891B2")
    _add_inline_formatted(
        cover_box,
        "**Leitfrage dieses Dokuments:** Wie entsteht aus dem Bauplan der einfachsten biologischen Zelle "
        "ein sich selbst regulierender digitaler Wirtschaftsorganismus, der statt ständiger Detailkontrolle "
        "(**~490 Stunden Ingenieurs-Aufwand**) durch Saat, Pflege und Ernte (**~15,9 Stunden Gärtner-Aufwand**) "
        "ein Vielfaches an Ertrag pro menschlicher Aufmerksamkeitsstunde erzielt?",
    )
    doc.add_page_break()

    i = 0
    img_re = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
    in_code = False
    code_buf: list[str] = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(8)
                _set_paragraph_shading(p, "F1F5F9", "64748B")
                r = p.add_run("\n".join(code_buf))
                r.font.name = "Consolas"
                r.font.size = Pt(8.8)
                r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            i += 1
            continue

        if in_code:
            code_buf.append(raw)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        # Bildzeile
        m_img = img_re.match(stripped)
        if m_img:
            alt_text, rel_path = m_img.group(1), m_img.group(2)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.is_file():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(3)
                p_img.paragraph_format.keep_with_next = True
                p_img.add_run().add_picture(str(img_path), width=Inches(6.2))

                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_after = Pt(10)
                rc = p_cap.add_run(alt_text)
                rc.italic = True
                rc.font.size = Pt(9.2)
                rc.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
            i += 1
            continue

        # Markdown-Tabelle
        if stripped.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            table_lines: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_str = lines[i].strip().strip("|")
                cells = [c.strip() for c in row_str.split("|")]
                # Trennzeile (---) überspringen
                if not all(set(c.replace(":", "").replace("-", "").strip()) == set() for c in cells):
                    table_lines.append(cells)
                i += 1
            if table_lines:
                cols = max(len(r) for r in table_lines)
                tbl = doc.add_table(rows=len(table_lines), cols=cols)
                tbl.style = "Table Grid"
                for r_idx, row_vals in enumerate(table_lines):
                    for c_idx in range(cols):
                        val = row_vals[c_idx] if c_idx < len(row_vals) else ""
                        cell = tbl.cell(r_idx, c_idx)
                        p = cell.paragraphs[0]
                        p.paragraph_format.space_before = Pt(2)
                        p.paragraph_format.space_after = Pt(2)
                        if r_idx == 0:
                            _set_cell_bg(cell, "0F1A2E")
                            run = p.add_run(val)
                            run.bold = True
                            run.font.size = Pt(9.2)
                            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                        else:
                            if r_idx % 2 == 0:
                                _set_cell_bg(cell, "F8FAFC")
                            _add_inline_formatted(p, val)
                            for r in p.runs:
                                r.font.size = Pt(9.2)
                spacer = doc.add_paragraph()
                spacer.paragraph_format.space_after = Pt(4)
            continue

        # Überschriften
        if stripped.startswith("# "):
            h = doc.add_heading(stripped[2:].strip(), level=1)
            for run in h.runs:
                run.font.color.rgb = RGBColor(0x0B, 0x3B, 0x5B)
                run.font.size = Pt(18)
            i += 1
            continue
        if stripped.startswith("## "):
            h = doc.add_heading(stripped[3:].strip(), level=2)
            for run in h.runs:
                run.font.color.rgb = RGBColor(0x0E, 0x74, 0x90)
                run.font.size = Pt(14)
            i += 1
            continue
        if stripped.startswith("### "):
            h = doc.add_heading(stripped[4:].strip(), level=3)
            for run in h.runs:
                run.font.color.rgb = RGBColor(0x06, 0x5F, 0x46)
                run.font.size = Pt(11.5)
            i += 1
            continue

        # Blockquote / Callout
        if stripped.startswith("> "):
            q_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                q_lines.append(lines[i].strip()[2:])
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            _set_paragraph_shading(p, "F0FDF4", "10B981")
            _add_inline_formatted(p, " ".join(q_lines))
            continue

        # Bullet-Listen
        if stripped.startswith("- ") or stripped.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            _add_inline_formatted(p, stripped[2:])
            i += 1
            continue

        # Nummerierte Listen
        m_num = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m_num:
            p = doc.add_paragraph(style="List Number")
            p.paragraph_format.space_after = Pt(2)
            _add_inline_formatted(p, m_num.group(2))
            i += 1
            continue

        # Normaler Absatz
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        _add_inline_formatted(p, stripped)
        i += 1

    out_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_docx))
    return len(doc.inline_shapes)


def build_html(md_path: Path = MD_PATH, out_html: Path = OUT_HTML) -> int:
    """Erzeugt eine saubere, eigenständige HTML-Ausgabe mit allen 50 Illustrationen."""
    import html as html_lib

    lines = md_path.read_text(encoding="utf-8").splitlines()
    img_re = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
    parts: list[str] = [
        "<!doctype html><html lang='de'><head><meta charset='utf-8'>",
        "<title>PROKARYONT — Das Organische Unternehmen</title>",
        "<style>",
        "body{font-family:Inter,Segoe UI,Arial,sans-serif;max-width:920px;margin:40px auto;padding:0 24px;color:#1e293b;line-height:1.65;}",
        "h1{color:#0b3b5b;border-bottom:2px solid #0891b2;padding-bottom:8px;}",
        "h2{color:#0e7490;margin-top:36px;} h3{color:#065f46;}",
        "figure{margin:24px 0;text-align:center;} figure img{max-width:100%;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,0.18);}",
        "figcaption{font-size:0.9rem;color:#475569;font-style:italic;margin-top:6px;}",
        "table{border-collapse:collapse;width:100%;margin:16px 0;font-size:0.92rem;}",
        "th{background:#0f1a2e;color:#fff;text-align:left;padding:8px 10px;} td{border:1px solid #cbd5e1;padding:7px 10px;}",
        "blockquote{background:#f0fdf4;border-left:4px solid #10b981;margin:14px 0;padding:10px 14px;}",
        "code{background:#f1f5f9;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace;color:#0e7490;}",
        "</style></head><body>",
    ]
    img_count = 0
    i = 0

    def _inline_html(s: str) -> str:
        esc = html_lib.escape(s)
        esc = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc)
        esc = re.sub(r"`([^`]+)`", r"<code>\1</code>", esc)
        esc = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", esc)
        return esc

    while i < len(lines):
        st = lines[i].strip()
        if not st or st == "---":
            i += 1
            continue
        m = img_re.match(st)
        if m:
            alt, rel = m.group(1), m.group(2)
            # Relativ zu docs/
            rel_from_docs = rel.replace("docs/", "", 1) if rel.startswith("docs/") else f"../{rel}"
            img_count += 1
            parts.append(
                f"<figure><img src='{html_lib.escape(rel_from_docs)}' alt='{html_lib.escape(alt)}' />"
                f"<figcaption>{html_lib.escape(alt)}</figcaption></figure>"
            )
            i += 1
            continue
        if st.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c.replace(":", "").replace("-", "").strip()) == set() for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                parts.append("<table><thead><tr>" + "".join(f"<th>{_inline_html(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>")
                for row in rows[1:]:
                    parts.append("<tr>" + "".join(f"<td>{_inline_html(c)}</td>" for c in row) + "</tr>")
                parts.append("</tbody></table>")
            continue
        if st.startswith("# "):
            parts.append(f"<h1>{_inline_html(st[2:])}</h1>")
        elif st.startswith("## "):
            parts.append(f"<h2>{_inline_html(st[3:])}</h2>")
        elif st.startswith("### "):
            parts.append(f"<h3>{_inline_html(st[4:])}</h3>")
        elif st.startswith("> "):
            parts.append(f"<blockquote>{_inline_html(st[2:])}</blockquote>")
        elif st.startswith("- ") or st.startswith("* "):
            parts.append(f"<ul><li>{_inline_html(st[2:])}</li></ul>")
        elif re.match(r"^\d+\.\s+", st):
            parts.append(f"<p>{_inline_html(st)}</p>")
        else:
            parts.append(f"<p>{_inline_html(st)}</p>")
        i += 1

    parts.append("</body></html>")
    out_html.write_text("\n".join(parts), encoding="utf-8")
    return img_count


if __name__ == "__main__":
    count = build_docx()
    html_count = build_html()
    print(f"DOCX erstellt: {OUT_DOCX} (eingebettete Bilder: {count})")
    print(f"HTML erstellt: {OUT_HTML} (referenzierte Bilder: {html_count})")
