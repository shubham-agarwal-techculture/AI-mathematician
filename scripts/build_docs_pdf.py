#!/usr/bin/env python3
"""Assemble the Aimath Reference Book from numbered chapters only.

The PDF is one continuous work. Standalone manuals under docs/ are not
appended here; that used to make the book short and incoherent.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DIST = DOCS / "dist"

# Reading order of the book. Do not insert standalone pamphlets here.
SOURCES: list[str] = [
    "book/01_preface.md",
    "book/02_vision.md",
    "book/03_installation.md",
    "book/04_configuration.md",
    "book/05_proving.md",
    "book/06_knowledge.md",
    "book/07_systems_research_reports.md",
    "book/08_host_distribution.md",
    "book/09_audiences_digest.md",
    "book/10_extension_maintenance.md",
    "book/11_reference_tables.md",
    "book/12_afterword.md",
    "book/13_prove_command.md",
    "book/14_search_explore_swarm.md",
    "book/15_curious_research_systems_report.md",
    "book/16_serve_worker.md",
    "book/17_statuses.md",
    "book/18_novelty_honesty.md",
    "book/19_personalities.md",
    "book/20_host_budget.md",
    "book/21_architecture_source.md",
    "book/22_audiences.md",
    "book/23_maintenance_extension.md",
    "book/24_limits.md",
    "book/25_afterword.md",
    "book/26_appendix_failures.md",
    "book/27_appendix_glossary.md",
    "book/28_appendix_tables.md",
    "book/29_how_to_write_a_statement.md",
    "book/30_worked_session.md",
]


def strip_md_links(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    return escape(text, {"\"": "&quot;"})


def assemble_markdown() -> str:
    parts = [
        "# Aimath Reference Book\n",
        "\n",
        "The model proposes. Lean decides. Mathlib is the trusted library. "
        "Everything else is a hint. Local novelty is not a claim of a new "
        "mathematical truth.\n",
        "\n",
        "Read from Chapter 1 forward. This file is the concatenated source of "
        "the numbered book only.\n",
        "\n",
        "---\n\n",
    ]
    for rel in SOURCES:
        path = DOCS / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        body = path.read_text(encoding="utf-8").strip() + "\n"
        parts.append(f"\n\n<!-- source: {rel} -->\n\n")
        parts.append(body)
        parts.append("\n\n---\n")
    return "".join(parts)


def render_pdf(markdown: str, pdf_path: Path) -> None:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "BookTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=16,
        leading=24,
    )
    h1 = ParagraphStyle(
        "BookH1",
        parent=styles["Heading1"],
        fontSize=14,
        spaceBefore=14,
        spaceAfter=8,
        leading=18,
    )
    h2 = ParagraphStyle(
        "BookH2",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=11,
        spaceAfter=6,
        leading=15,
    )
    h3 = ParagraphStyle(
        "BookH3",
        parent=styles["Heading3"],
        fontSize=11,
        spaceBefore=9,
        spaceAfter=5,
        leading=14,
    )
    body = ParagraphStyle(
        "BookBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=7,
        alignment=4,  # justify
    )
    code = ParagraphStyle(
        "BookCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        leftIndent=4,
        spaceBefore=3,
        spaceAfter=7,
    )
    bullet = ParagraphStyle(
        "BookBullet",
        parent=body,
        leftIndent=16,
        spaceAfter=3,
        alignment=0,
    )

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Times-Roman", 8)
        canvas.drawString(0.85 * inch, 0.45 * inch, "Aimath Reference Book")
        canvas.drawRightString(LETTER[0] - 0.85 * inch, 0.45 * inch, str(doc.page))
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.65 * inch,
        title="Aimath Reference Book",
        author="aimath documentation",
    )
    story: list = []
    in_code = False
    code_lines: list[str] = []
    first_h1 = True

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            story.append(Preformatted("\n".join(code_lines)[:8000], code))
            code_lines = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip("\n")
        if line.strip().startswith("<!--"):
            continue
        if line.strip().startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_code()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.strip() == "---":
            story.append(Spacer(1, 6))
            continue
        if line.startswith("# "):
            if not first_h1:
                story.append(PageBreak())
            first_h1 = False
            heading = strip_md_links(line[2:])
            style = title if "Reference Book" in line or line.startswith("# Chapter") or line.startswith("# Appendix") else h1
            if line.startswith("# Chapter") or line.startswith("# Appendix"):
                style = title
            story.append(Paragraph(heading, style))
            continue
        if line.startswith("## "):
            story.append(Paragraph(strip_md_links(line[3:]), h2))
            continue
        if line.startswith("### "):
            story.append(Paragraph(strip_md_links(line[4:]), h3))
            continue
        if re.match(r"^\|.+\|", line):
            story.append(Preformatted(re.sub(r"[`*]", "", line)[:200], code))
            continue
        if re.match(r"^[-*] ", line):
            story.append(Paragraph("• " + strip_md_links(line[2:]), bullet))
            continue
        if re.match(r"^\d+\. ", line):
            story.append(Paragraph(strip_md_links(line), bullet))
            continue
        if not line.strip():
            story.append(Spacer(1, 3))
            continue
        story.append(Paragraph(strip_md_links(line), body))

    flush_code()
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    markdown = assemble_markdown()
    md_path = DIST / "Aimath_Reference_Book.md"
    pdf_path = DIST / "Aimath_Reference_Book.pdf"
    md_path.write_text(markdown, encoding="utf-8")
    render_pdf(markdown, pdf_path)
    print(f"wrote {md_path}")
    print(f"wrote {pdf_path}")
    print(f"markdown characters: {len(markdown)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
