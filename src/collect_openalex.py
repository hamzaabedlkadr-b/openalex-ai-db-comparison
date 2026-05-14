"""Collect and normalize a small OpenAlex works dataset.

The script intentionally uses only the Python standard library so the first
project milestone can run without dependency setup.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://api.openalex.org/works"
DEFAULT_TERMS = [
    "retrieval augmented generation",
    "large language models",
    "artificial intelligence",
    "machine learning",
]
DEFAULT_FILTER = "from_publication_date:2018-01-01,type:article"


def short_openalex_id(value: str | None) -> str:
    if not value:
        return ""
    return value.rstrip("/").split("/")[-1]


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    if not inverted_index:
        return ""

    positioned_words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for position in positions:
            positioned_words.append((position, word))

    if not positioned_words:
        return ""

    max_position = max(position for position, _ in positioned_words)
    words = [""] * (max_position + 1)
    for position, word in positioned_words:
        words[position] = word
    return " ".join(word for word in words if word).strip()


def request_page(
    *,
    search_term: str,
    cursor: str,
    per_page: int,
    filters: str,
    mailto: str | None,
) -> dict[str, Any]:
    params = {
        "search": search_term,
        "filter": filters,
        "per-page": str(per_page),
        "cursor": cursor,
    }
    if mailto:
        params["mailto"] = mailto

    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"openalex-ai-db-comparison/0.1 ({mailto or 'student project'})",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAlex request failed with HTTP {error.code}: {details}") from error


def collect_works(
    *,
    terms: list[str],
    per_term: int,
    per_page: int,
    filters: str,
    mailto: str | None,
    pause_seconds: float,
) -> dict[str, dict[str, Any]]:
    works: dict[str, dict[str, Any]] = {}

    for term in terms:
        cursor = "*"
        collected_for_term = 0

        while collected_for_term < per_term:
            page = request_page(
                search_term=term,
                cursor=cursor,
                per_page=min(per_page, per_term - collected_for_term),
                filters=filters,
                mailto=mailto,
            )

            results = page.get("results", [])
            if not results:
                break

            for work in results:
                work_id = short_openalex_id(work.get("id"))
                if not work_id:
                    continue

                existing = works.setdefault(work_id, work)
                matched_terms = set(existing.get("_matched_search_terms", []))
                matched_terms.add(term)
                existing["_matched_search_terms"] = sorted(matched_terms)
                collected_for_term += 1

                if collected_for_term >= per_term:
                    break

            next_cursor = page.get("meta", {}).get("next_cursor")
            if not next_cursor or next_cursor == cursor:
                break

            cursor = next_cursor
            time.sleep(pause_seconds)

    return works


def extract_topic_rows(work: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    paper_id = short_openalex_id(work.get("id"))
    topics: dict[str, dict[str, str]] = {}
    paper_topics: dict[tuple[str, str], dict[str, str]] = {}

    def add_topic(topic: dict[str, Any] | None, source: str) -> None:
        if not topic:
            return
        topic_id = short_openalex_id(topic.get("id"))
        topic_name = topic.get("display_name") or topic.get("name") or ""
        if not topic_id or not topic_name:
            return
        topics[topic_id] = {
            "topic_id": topic_id,
            "display_name": topic_name,
        }
        paper_topics[(paper_id, topic_id)] = {
            "paper_id": paper_id,
            "topic_id": topic_id,
            "score": str(topic.get("score", "")),
            "source": source,
        }

    add_topic(work.get("primary_topic"), "primary_topic")

    for topic in work.get("topics") or []:
        add_topic(topic, "topic")

    # Some OpenAlex records still expose concepts, so keep this as a fallback.
    for concept in work.get("concepts") or []:
        add_topic(concept, "concept")

    return list(topics.values()), list(paper_topics.values())


def normalize_works(works: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    collected_ids = set(works.keys())
    papers: list[dict[str, str]] = []
    authors: dict[str, dict[str, str]] = {}
    paper_authors: dict[tuple[str, str], dict[str, str]] = {}
    topics: dict[str, dict[str, str]] = {}
    paper_topics: dict[tuple[str, str, str], dict[str, str]] = {}
    citations: list[dict[str, str]] = []

    for paper_id, work in sorted(works.items()):
        primary_topic = work.get("primary_topic") or {}
        primary_topic_id = short_openalex_id(primary_topic.get("id"))

        papers.append(
            {
                "paper_id": paper_id,
                "title": work.get("display_name") or work.get("title") or "",
                "publication_year": str(work.get("publication_year") or ""),
                "publication_date": work.get("publication_date") or "",
                "cited_by_count": str(work.get("cited_by_count") or 0),
                "doi": work.get("doi") or "",
                "openalex_url": work.get("id") or "",
                "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
                "primary_topic_id": primary_topic_id,
                "primary_topic_name": primary_topic.get("display_name") or "",
                "matched_search_terms": "; ".join(work.get("_matched_search_terms", [])),
            }
        )

        for authorship in work.get("authorships") or []:
            author = authorship.get("author") or {}
            author_id = short_openalex_id(author.get("id"))
            if not author_id:
                continue

            authors[author_id] = {
                "author_id": author_id,
                "display_name": author.get("display_name") or "",
            }
            paper_authors[(paper_id, author_id)] = {
                "paper_id": paper_id,
                "author_id": author_id,
                "author_position": authorship.get("author_position") or "",
                "is_corresponding": str(bool(authorship.get("is_corresponding"))).lower(),
            }

        work_topics, work_paper_topics = extract_topic_rows(work)
        for topic in work_topics:
            topics[topic["topic_id"]] = topic
        for row in work_paper_topics:
            paper_topics[(row["paper_id"], row["topic_id"], row["source"])] = row

        for cited_work in work.get("referenced_works") or []:
            cited_paper_id = short_openalex_id(cited_work)
            if cited_paper_id in collected_ids:
                citations.append(
                    {
                        "citing_paper_id": paper_id,
                        "cited_paper_id": cited_paper_id,
                    }
                )

    return {
        "papers": papers,
        "authors": sorted(authors.values(), key=lambda row: row["author_id"]),
        "paper_authors": sorted(paper_authors.values(), key=lambda row: (row["paper_id"], row["author_id"])),
        "topics": sorted(topics.values(), key=lambda row: row["topic_id"]),
        "paper_topics": sorted(paper_topics.values(), key=lambda row: (row["paper_id"], row["topic_id"], row["source"])),
        "citations": sorted(citations, key=lambda row: (row["citing_paper_id"], row["cited_paper_id"])),
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect and normalize OpenAlex AI paper data.")
    parser.add_argument("--raw-output", default="data/raw/openalex_works.jsonl")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--per-term", type=int, default=100, help="Maximum works to collect for each search term.")
    parser.add_argument("--per-page", type=int, default=100, help="OpenAlex page size, maximum 200.")
    parser.add_argument("--filter", default=DEFAULT_FILTER, help="OpenAlex filter expression.")
    parser.add_argument("--mailto", default=None, help="Optional email for OpenAlex polite pool.")
    parser.add_argument("--pause", type=float, default=0.2, help="Pause between paginated requests.")
    parser.add_argument("--terms", nargs="+", default=DEFAULT_TERMS, help="Search terms to collect.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.per_page < 1 or args.per_page > 200:
        raise SystemExit("--per-page must be between 1 and 200")
    if args.per_term < 1:
        raise SystemExit("--per-term must be at least 1")

    works = collect_works(
        terms=args.terms,
        per_term=args.per_term,
        per_page=args.per_page,
        filters=args.filter,
        mailto=args.mailto,
        pause_seconds=args.pause,
    )

    raw_output = Path(args.raw_output)
    write_jsonl(raw_output, list(works.values()))

    processed_dir = Path(args.processed_dir)
    normalized = normalize_works(works)
    write_csv(
        processed_dir / "papers.csv",
        normalized["papers"],
        [
            "paper_id",
            "title",
            "publication_year",
            "publication_date",
            "cited_by_count",
            "doi",
            "openalex_url",
            "abstract",
            "primary_topic_id",
            "primary_topic_name",
            "matched_search_terms",
        ],
    )
    write_csv(processed_dir / "authors.csv", normalized["authors"], ["author_id", "display_name"])
    write_csv(
        processed_dir / "paper_authors.csv",
        normalized["paper_authors"],
        ["paper_id", "author_id", "author_position", "is_corresponding"],
    )
    write_csv(processed_dir / "topics.csv", normalized["topics"], ["topic_id", "display_name"])
    write_csv(
        processed_dir / "paper_topics.csv",
        normalized["paper_topics"],
        ["paper_id", "topic_id", "score", "source"],
    )
    write_csv(
        processed_dir / "citations.csv",
        normalized["citations"],
        ["citing_paper_id", "cited_paper_id"],
    )

    print(f"Collected {len(works)} unique works")
    print(f"Wrote raw data to {raw_output}")
    print(f"Wrote processed CSV files to {processed_dir}")
    for name, rows in normalized.items():
        print(f"- {name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
