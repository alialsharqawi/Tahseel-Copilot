#!/usr/bin/env python3
"""Build the LMS documentation PDF from the Markdown parts in docs/lms/parts.

The LMS submission links to the PDF in the repository root, so the default output is
    Tahseel_Project_Documentation_v1.pdf   (in the repository root, same name, overwritten in place)
Never rename or move that file.

Needs:  pip install markdown
Plus ONE of:  pip install weasyprint            (best page numbers; needs the Pango system library)
              a Chrome, Chromium, or Brave browser installed (used in headless mode)

Run from the repository root:
    python tools/build_docs_pdf.py --check                  # list parts and images, build nothing
    python tools/build_docs_pdf.py --output /tmp/try.pdf    # a trial build that does not touch the real PDF
    python tools/build_docs_pdf.py                          # overwrite the root PDF (a backup goes to _private/pdf_backups)
"""
import argparse
import csv
import datetime
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS_DIR = ROOT / "docs" / "lms" / "parts"
DEFAULT_OUTPUT = ROOT / "Tahseel_Project_Documentation_v1.pdf"
BACKUP_DIR = ROOT / "_private" / "pdf_backups"
WIDE_IMAGES = {"architecture_logical.png", "request_flow.png", "deployment.png", "ui_flow.png", "stakeholder_map.png"}
BROWSERS = ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "brave-browser", "brave"]

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
        @bottom-center { content: counter(page); font: 9pt 'DejaVu Sans', Arial, sans-serif; color: #758675; }
        @bottom-left { content: "Tahseel AI: Project Documentation"; font: 8pt 'DejaVu Sans', Arial, sans-serif; color: #9bad9c; } }
@page wide { size: A4 landscape; margin: 12mm; }
@page cover { margin: 0; @bottom-center { content: none; } @bottom-left { content: none; } }
body { font-family: 'Noto Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #1f2933; }
h1 { font-size: 22pt; color: #1f5b43; border-bottom: 2px solid #1f5b43; padding-bottom: 4pt; page-break-before: always; margin-top: 0; }
h2 { font-size: 14pt; color: #28654a; margin-top: 16pt; page-break-after: avoid; }
h3 { font-size: 11.5pt; color: #4d634f; margin-top: 12pt; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 8.6pt; }
th, td { border: 1px solid #c5d2c7; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #e8efe8; }
tr { page-break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.6pt; background: #f3f5f7; padding: 0 2pt; }
pre { background: #f3f5f7; border: 1px solid #cfd8dc; padding: 6pt; font-size: 8pt; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { border-left: 3px solid #b78a3f; margin: 8pt 0; padding: 2pt 10pt; color: #455249; background: #faf7ef; }
figure { margin: 8pt 0; text-align: center; }
figure img { max-width: 100%; max-height: 230mm; }
figure.wide { page: wide; page-break-before: always; page-break-after: always; margin: 0; }
figure.wide img { max-width: 100%; max-height: 180mm; }
.cover { page: cover; position: relative; height: 259mm; overflow: hidden; page-break-after: always; padding: 20mm 22mm 18mm; box-sizing: border-box; background: #173d2e; color: #f8f5ed; }
.cover::before { content: ""; position: absolute; inset: 0 0 auto; height: 4mm; background: #c99a45; }
.cover::after { content: ""; position: absolute; top: 24mm; right: -24mm; width: 82mm; height: 82mm; border: 1px solid #456653; border-radius: 50%; }
.cover-topline, .cover-footer, .cover-team-heading, .cover-team-list li { display: flex; align-items: center; justify-content: space-between; }
.cover-topline { position: relative; z-index: 1; color: #e1c27d; font-size: 9pt; letter-spacing: 0.7pt; text-transform: uppercase; }
.cover-brand { font-weight: bold; }
.cover-main { position: relative; z-index: 1; margin-top: 42mm; }
.cover-eyebrow { color: #e1c27d; font-size: 9pt !important; letter-spacing: 1pt; text-transform: uppercase; }
.cover h1 { color: #fff; border: none; font-size: 42pt; page-break-before: avoid; margin: 4mm 0 2mm; }
.cover-subtitle { max-width: 135mm; font-size: 14pt !important; line-height: 1.5; color: #d7e3d9 !important; }
.cover-team { margin-top: 14mm; padding: 8mm 9mm; background: #204a38; border-left: 3px solid #c99a45; }
.cover-team h2 { margin: 0; color: #fff; font-size: 14pt; }
.cover-team-count { color: #e1c27d; font-size: 9pt; }
.cover-team-list { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm 8mm; list-style: none; margin: 6mm 0 0; padding: 0; }
.cover-team-list li { justify-content: flex-start; min-height: 11mm; border-top: 1px solid #496957; padding-top: 2mm; color: #f8f5ed; }
.cover-team-list li::before { content: ""; width: 2.2mm; height: 2.2mm; flex: 0 0 auto; margin-right: 3mm; border-radius: 50%; background: #c99a45; }
.cover-team-list .team-name { flex: 1; }
.cover-team-list .team-role { margin-left: 2mm; color: #e1c27d; font-size: 8pt; }
.cover-footer { position: absolute; z-index: 1; right: 22mm; bottom: 18mm; left: 22mm; gap: 8mm; display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #496957; padding-top: 5mm; color: #c9d8cd; font-size: 8pt; }
.cover-repo { max-width: 125mm; overflow-wrap: anywhere; text-align: right; }
.toc h1 { page-break-before: auto; }
.toc ul { list-style: none; padding-left: 0; }
.toc ul ul { padding-left: 16pt; font-size: 9pt; }
.toc li { margin: 2pt 0; }
.toc a { color: #1f2933; text-decoration: none; }
.toc a::after { content: leader('.') target-counter(attr(href), page); color: #758675; }
.toc .part > a { font-weight: bold; font-size: 11pt; }
"""


def need_markdown():
    try:
        import markdown  # noqa: F401
    except ImportError:
        raise SystemExit("The 'markdown' package is missing. Install it with:  pip install markdown")


def find_parts():
    return sorted(PARTS_DIR.glob("[0-9][0-9]_*.md"))


def part_title(text, fallback):
    m = re.search(r"^#\s+(.+)$", text, flags=re.M)
    return m.group(1).strip() if m else fallback


def read_team_leader():
    try:
        t = (ROOT / "TEAM.md").read_text(encoding="utf-8")
        m = re.search(r"\*\*Team Leader[^*]*\*\*\s*(.+)", t)
        if m:
            return re.split(r"\(", m.group(1))[0].strip()
    except OSError:
        pass
    return ""


def read_team_members():
    roster = ROOT / "docs" / "team" / "skills.csv"
    try:
        with roster.open(encoding="utf-8", newline="") as f:
            members = [row["member"].strip() for row in csv.DictReader(f)
                       if row.get("member", "").strip()]
    except OSError as exc:
        raise SystemExit(f"Could not read the team roster at {roster}: {exc}") from exc
    if not members:
        raise SystemExit(f"No team members found in {roster}")
    return members


def read_repo_url():
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout.strip()
        return re.sub(r"\.git$", "", out)
    except Exception:
        return ""


def convert_part(index, path, warnings):
    import markdown
    from markdown.extensions.toc import slugify as default_slugify

    prefix = f"p{index:02d}"
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"],
                           extension_configs={"toc": {"slugify": lambda v, s: f"{prefix}-{default_slugify(v, s)}"}})
    text = path.read_text(encoding="utf-8")
    body = md.convert(text)

    def fix_img(m):
        alt, src = m.group(1), m.group(2)
        target = (path.parent / src).resolve()
        if not target.exists():
            warnings.append(f"{path.name}: image not found: {src}")
            return m.group(0)
        wide = target.name in WIDE_IMAGES or "wireframes" in target.parts
        cls = ' class="wide"' if wide else ""
        return f'<figure{cls}><img alt="{alt}" src="{target.as_uri()}"></figure>'

    body = re.sub(r'<p>\s*<img alt="(.*?)" src="(.*?)"\s*/?>\s*</p>', fix_img, body)
    return body, md.toc_tokens, part_title(text, path.stem)


def toc_html(entries):
    out = ['<div class="toc"><h1>Contents</h1><ul>']
    for anchor, title, tokens in entries:
        out.append(f'<li class="part"><a href="#{anchor}">{html.escape(title)}</a><ul>')
        for t in tokens:
            for ch in t.get("children", []):
                out.append(f'<li><a href="#{ch["id"]}">{html.escape(ch["name"])}</a></li>')
        out.append("</ul></li>")
    out.append("</ul></div>")
    return "\n".join(out)


def build_html(parts, warnings):
    sections, entries = [], []
    for i, p in enumerate(parts):
        body, tokens, title = convert_part(i + 1, p, warnings)
        first = tokens[0]["id"] if tokens else f"p{i + 1:02d}"
        entries.append((first, title, tokens))
        sections.append(body)
    leader = read_team_leader()
    members = read_team_members()
    repo = read_repo_url()
    team_items = []
    for member in members:
        role = '<span class="team-role">Team Leader</span>' if member == leader else ""
        team_items.append(f'<li><span class="team-name">{html.escape(member)}</span>{role}</li>')
    cover = ('<div class="cover">'
             '<div class="cover-topline"><span class="cover-brand">Tahseel AI</span><span>DEPI Graduation Project</span></div>'
             '<div class="cover-main"><p class="cover-eyebrow">Project Documentation</p><h1>Tahseel AI</h1>'
             '<p class="cover-subtitle">An agentic credit-control copilot for Egyptian B2B distributors.</p>'
             '<section class="cover-team"><div class="cover-team-heading"><h2>Project Team</h2>'
             f'<span class="cover-team-count">{len(members)} members</span></div>'
             f'<ul class="cover-team-list">{"".join(team_items)}</ul></section></div>'
             '<div class="cover-footer"><span>DEPI Graduation Project</span>'
             + (f'<span class="cover-repo">{html.escape(repo)}</span>' if repo else "") + '</div></div>')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Tahseel AI: Project Documentation</title>'
            f"<style>{CSS}</style></head><body>{cover}{toc_html(entries)}{''.join(sections)}</body></html>")


def find_browser(explicit):
    if explicit:
        return explicit
    for name in BROWSERS:
        p = shutil.which(name)
        if p:
            return p
    return None


def render_pdf(html_path, out_path, engine, browser):
    if engine in ("auto", "weasyprint"):
        try:
            from weasyprint import HTML
            HTML(filename=str(html_path)).write_pdf(str(out_path))
            return "weasyprint"
        except ImportError:
            if engine == "weasyprint":
                raise SystemExit("weasyprint is not installed. Install it with:  pip install weasyprint")
    b = find_browser(browser)
    if not b:
        raise SystemExit("No PDF engine found. Install one of:\n  pip install weasyprint\n  or a Chrome / Chromium / Brave browser (or pass --browser /path/to/browser)")
    cmd = [b, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
           f"--print-to-pdf={out_path}", html_path.as_uri()]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        cmd.insert(1, "--no-sandbox")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise SystemExit(f"The browser did not produce a PDF.\n{r.stderr[-800:]}")
    return f"browser ({Path(b).name})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", help=f"output PDF (default: {DEFAULT_OUTPUT.name} in the repository root)")
    ap.add_argument("--engine", choices=["auto", "weasyprint", "browser"], default="auto")
    ap.add_argument("--browser", help="path to a Chrome, Chromium, or Brave executable")
    ap.add_argument("--check", action="store_true", help="list the parts and check the images; build nothing")
    ap.add_argument("--no-backup", action="store_true", help="do not back up an existing PDF before overwriting it")
    args = ap.parse_args()

    need_markdown()
    parts = find_parts()
    if not parts:
        raise SystemExit(f"No parts found in {PARTS_DIR}")
    expected = {f"{i:02d}" for i in range(1, 7)}
    missing = sorted(expected - {p.name[:2] for p in parts})
    warnings = []
    html_text = build_html(parts, warnings)
    print("Parts:")
    for p in parts:
        print(f"  {p.name}")
    if missing:
        print(f"WARNING: parts not found yet: {', '.join(missing)}")
    for w in warnings:
        print("WARNING:", w)
    if args.check:
        print(f"Check done: {len(parts)} parts, {len(warnings)} image warnings.")
        return 1 if warnings else 0

    out = Path(args.output).resolve() if args.output else DEFAULT_OUTPUT
    if out == DEFAULT_OUTPUT and out.exists() and not args.no_backup:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(out, BACKUP_DIR / f"{stamp}_{out.name}")
        print(f"Backed up the existing PDF to {BACKUP_DIR}")
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "doc.html"
        html_path.write_text(html_text, encoding="utf-8")
        tmp_pdf = Path(tmp) / "out.pdf"
        used = render_pdf(html_path, tmp_pdf, args.engine, args.browser)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_pdf), str(out))
    pages = ""
    try:
        from pypdf import PdfReader
        pages = f", {len(PdfReader(str(out)).pages)} pages"
    except Exception:
        pass
    print(f"Wrote {out} using {used}{pages}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
