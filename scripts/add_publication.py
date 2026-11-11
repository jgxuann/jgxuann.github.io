#!/usr/bin/env python3
"""Add a DOI or arXiv paper, assign the next J/C number, and rebuild BibTeX."""

import argparse
import json
import re
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "publications.json"


def request_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "GuanxuanJiangHomepage/1.0 (mailto:gjiang240@connect.hkust-gz.edu.cn)"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def next_identifier(publications, category):
    prefix = "J" if category == "journal" else "C"
    used = [int(match.group(1)) for publication in publications if (match := re.fullmatch(prefix + r"(\d+)", publication["id"]))]
    return f"{prefix}{max(used, default=0) + 1}"


def people(authors):
    return [" ".join(part for part in (author.get("given"), author.get("family")) if part) for author in authors]


def from_doi(doi, category):
    item = request_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))["message"]
    date_parts = item.get("published-print", item.get("published-online", item.get("issued", {}))).get("date-parts", [[None]])[0]
    title = item.get("title", [""])[0]
    return {
        "category": category,
        "cite_key": f"{(item.get('author') or [{}])[0].get('family', 'unknown').lower()}{date_parts[0]}{re.sub(r'[^a-z0-9]+', '', title.lower().split()[0])}",
        "title": title,
        "authors": people(item.get("author", [])),
        "venue": (item.get("container-title") or [""])[0],
        "year": date_parts[0],
        "volume": item.get("volume", ""),
        "number": item.get("issue", ""),
        "pages": item.get("page", ""),
        "doi": item["DOI"],
        "url": item.get("URL", "https://doi.org/" + item["DOI"]),
    }


def from_arxiv(arxiv_id, category):
    xml_url = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv_id)
    with urllib.request.urlopen(xml_url, timeout=20) as response:
        root = ET.parse(response).getroot()
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", namespace)
    title = " ".join(entry.findtext("atom:title", default="", namespaces=namespace).split())
    published = entry.findtext("atom:published", default="", namespaces=namespace)
    authors = [" ".join(author.findtext("atom:name", default="", namespaces=namespace).split()) for author in entry.findall("atom:author", namespace)]
    return {
        "category": category,
        "cite_key": f"{authors[0].split()[-1].lower()}{published[:4]}{re.sub(r'[^a-z0-9]+', '', title.lower().split()[0])}",
        "title": title,
        "authors": authors,
        "venue": "arXiv",
        "year": int(published[:4]),
        "arxiv": arxiv_id,
        "url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", choices=("journal", "conference"), required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--doi")
    source.add_argument("--arxiv")
    arguments = parser.parse_args()
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    publication = from_doi(arguments.doi, arguments.category) if arguments.doi else from_arxiv(arguments.arxiv, arguments.category)
    publication["id"] = next_identifier(data["publications"], arguments.category)
    data["publications"].append(publication)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run(["python3", str(ROOT / "scripts" / "generate_bibtex.py")], check=True)
    print(f"Added [{publication['id']}] {publication['title']}")


if __name__ == "__main__":
    main()
