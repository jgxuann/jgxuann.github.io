"""Export per-paper citation counts from Guanxuan Jiang's Google Scholar profile."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from scholarly import scholarly


PROFILE_ID = os.getenv("GOOGLE_SCHOLAR_PROFILE_ID", "IaBa8RAAAAAJ")
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "data" / "google-scholar-citations.json"

# GitHub-hosted runners are often rate-limited by Google Scholar.  Fail quickly
# with useful logs instead of leaving the workflow waiting through many retries.
scholarly.set_timeout(10)
scholarly.set_retries(2)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print(f"Fetching Google Scholar profile {PROFILE_ID}...")
    author = scholarly.search_author_id(PROFILE_ID)
    author = scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])

    papers = {}
    for publication in author.get("publications", []):
        bibliographic_data = publication.get("bib", {})
        title = bibliographic_data.get("title")
        if title:
            papers[title] = int(publication.get("num_citations", 0))

    payload = {
        "source": "Google Scholar",
        "profile_id": PROFILE_ID,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_citations": int(author.get("citedby", 0)),
        "papers": papers,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(papers)} paper citation counts to {OUTPUT}")


if __name__ == "__main__":
    main()
