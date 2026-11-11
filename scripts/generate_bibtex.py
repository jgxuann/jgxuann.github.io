#!/usr/bin/env python3
"""Generate the visitor-facing BibTeX page and downloadable .bib file."""

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "publications.json"
BIB_FILE = ROOT / "publications.bib"
HTML_FILE = ROOT / "bibtex.html"


def bibtex_entry(publication):
    entry_type = "@inproceedings" if publication["category"] == "conference" else "@article"
    venue_field = "booktitle" if entry_type == "@inproceedings" else "journal"
    fields = [("title", publication["title"]), ("author", " and ".join(publication["authors"])),
              (venue_field, publication["venue"]), ("year", str(publication["year"]))]
    for field in ("volume", "number", "pages", "doi", "url"):
        if publication.get(field):
            fields.append((field, publication[field]))
    if publication.get("arxiv"):
        fields.extend([("eprint", publication["arxiv"]), ("archivePrefix", "arXiv")])
    body = ",\n".join(f"  {key} = {{{value}}}" for key, value in fields)
    return f"{entry_type}{{{publication['cite_key']},\n{body}\n}}"


def page_item(publication):
    entry = bibtex_entry(publication)
    identifier = publication["id"].lower()
    return f'''    <section class="bib-item" id="{identifier}">
      <h2>[{html.escape(publication["id"])}] {html.escape(publication["title"])}</h2>
      <button class="copy-btn" type="button" data-copy-target="bib-{identifier}">Copy BibTeX</button>
      <pre id="bib-{identifier}">{html.escape(entry)}</pre>
    </section>'''


def main():
    publications = json.loads(DATA_FILE.read_text(encoding="utf-8"))["publications"]
    identifiers = [publication["id"] for publication in publications]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Publication IDs must be unique.")
    entries = [bibtex_entry(publication) for publication in publications]
    BIB_FILE.write_text("% Generated from data/publications.json. Do not edit manually.\n\n" + "\n\n".join(entries) + "\n", encoding="utf-8")
    sections = "\n\n".join(page_item(publication) for publication in publications)
    HTML_FILE.write_text(f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BibTeX | Guanxuan Jiang</title>
  <style>
    body {{ max-width: 900px; margin: 40px auto; padding: 0 20px; font: 16px/1.6 Arial, sans-serif; color: #222; }}
    h1 {{ margin-bottom: 4px; }}
    .intro {{ color: #666; margin-top: 0; }}
    .download {{ color: #377bb0; }}
    .bib-item {{ margin: 38px 0; scroll-margin-top: 24px; }}
    h2 {{ font-size: 1.1rem; margin-bottom: 10px; }}
    .copy-btn {{ margin-bottom: 12px; padding: 7px 12px; border: 1px solid #aaa; background: #fff; cursor: pointer; font-size: .9rem; }}
    .copy-btn:hover {{ background: #f5f5f5; }}
    pre {{ background: #f7f7f7; border: 1px solid #ddd; padding: 16px; overflow-x: auto; white-space: pre-wrap; word-break: break-word; font: .9rem/1.5 "Courier New", monospace; }}
  </style>
</head>
<body>
  <h1>BibTeX</h1>
  <p class="intro">Copy an individual record below, or <a class="download" href="publications.bib" download>download all BibTeX entries</a>.</p>
{sections}
  <script>
    document.querySelectorAll('[data-copy-target]').forEach((button) => {{
      button.addEventListener('click', async () => {{
        await navigator.clipboard.writeText(document.getElementById(button.dataset.copyTarget).innerText);
        const previous = button.textContent;
        button.textContent = 'Copied';
        setTimeout(() => {{ button.textContent = previous; }}, 1200);
      }});
    }});
  </script>
</body>
</html>
''', encoding="utf-8")
    print(f"Generated {BIB_FILE.relative_to(ROOT)} and {HTML_FILE.relative_to(ROOT)}.")


if __name__ == "__main__":
    main()
