"""Export per-paper citation counts from Guanxuan Jiang's Google Scholar profile."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROFILE_ID = os.getenv("GOOGLE_SCHOLAR_PROFILE_ID", "IaBa8RAAAAAJ")
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "data" / "google-scholar-citations.json"
PROFILE_URL = "https://scholar.google.com/citations"
PAGE_SIZE = 100
REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
)


def parse_count(value):
    """Convert Scholar's localized count text to an integer."""
    digits = "".join(character for character in value if character.isdigit())
    return int(digits or 0)


def parse_profile_page(html):
    """Return the total citation count and publications from one profile page."""
    soup = BeautifulSoup(html, "html.parser")
    if soup.select_one("#gsc_prf_in") is None:
        page_text = soup.get_text(" ", strip=True).lower()
        reason = "CAPTCHA/consent page" if "captcha" in page_text or "not a robot" in page_text else "unexpected page"
        raise RuntimeError(f"Google Scholar returned an {reason}; refusing to overwrite citation data")

    total_node = soup.select_one("#gsc_rsb_st .gsc_rsb_std")
    if total_node is None:
        raise RuntimeError("Google Scholar profile did not contain a total citation count")

    papers = {}
    for row in soup.select(".gsc_a_tr"):
        title_node = row.select_one(".gsc_a_at")
        if title_node is None:
            continue
        citation_node = row.select_one(".gsc_a_c .gsc_a_ac")
        papers[title_node.get_text(" ", strip=True)] = parse_count(
            citation_node.get_text(strip=True) if citation_node else "0"
        )

    return parse_count(total_node.get_text(strip=True)), papers


def fetch_profile(profile_id):
    """Fetch all publication rows without relying on scholarly's brittle parser."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})
    papers = {}
    total_citations = 0

    for start in range(0, 10_000, PAGE_SIZE):
        logging.info("Fetching Google Scholar publications starting at %d", start)
        response = session.get(
            PROFILE_URL,
            params={"hl": "en", "user": profile_id, "cstart": start, "pagesize": PAGE_SIZE},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        page_total, page_papers = parse_profile_page(response.text)
        if start == 0:
            total_citations = page_total
        papers.update(page_papers)
        if len(page_papers) < PAGE_SIZE:
            break
    else:
        raise RuntimeError("Google Scholar pagination exceeded the safety limit")

    return total_citations, papers


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print(f"Fetching Google Scholar profile {PROFILE_ID}...")
    total_citations, papers = fetch_profile(PROFILE_ID)

    payload = {
        "source": "Google Scholar",
        "profile_id": PROFILE_ID,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_citations": total_citations,
        "papers": papers,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(papers)} paper citation counts to {OUTPUT}")


if __name__ == "__main__":
    main()
