#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
knowledge_updater.py — self-improving knowledge pipeline for `art-antique-valuation`.

Fetches fresh signals from:
  * ArXiv RSS feeds (econ.GN, cs.CY, stat.AP)
  * Authoritative domain landing pages
  * Optional WebSearch backends (SerpApi, Bing) when API keys are supplied

Scores by recency × keyword relevance, deduplicates by URL+title hash, and appends
dated entries to SECOND-KNOWLEDGE-BRAIN.md.

Schedule: weekly cron.
Graceful degradation: exits 0 when network or APIs are unavailable so the skill
continues from the existing knowledge brain.
"""
import argparse
import datetime
import hashlib
import html
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BRAIN = os.path.normpath(os.path.join(HERE, "..", "SECOND-KNOWLEDGE-BRAIN.md"))

ARXIV_CATEGORIES = ["econ.GN", "cs.CY", "stat.AP"]
DOMAIN_SOURCES = [
    {"name": "Heritage Auctions", "url": "https://www.ha.com/"},
    {"name": "Christie's Results", "url": "https://www.christies.com/en/results"},
    {"name": "Art Loss Register", "url": "https://www.artloss.com/"},
    {"name": "PSA Price Guide", "url": "https://www.psacard.com/priceguide"},
    {"name": "Getty Provenance Index", "url": "https://www.getty.edu/research/tools/provenance/"},
]
DEFAULT_QUERIES = [
    "auction price index fine art 2026",
    "trading card grading population report trends",
    "provenance research methodology cultural property",
    "art market liquidity downturn report",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

log = logging.getLogger("knowledge_updater")


@dataclass(frozen=True)
class Entry:
    title: str
    authors: str
    date: str
    url: str
    abstract: str
    source: str = "unknown"
    source_type: str = "unknown"

    def fingerprint(self) -> str:
        payload = f"{self.url.strip().lower()}::{self.title.strip().lower()}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class Config:
    brain_path: str = DEFAULT_BRAIN
    arxiv_categories: List[str] = field(default_factory=lambda: list(ARXIV_CATEGORIES))
    domain_sources: List[Dict[str, str]] = field(default_factory=lambda: list(DOMAIN_SOURCES))
    search_queries: List[str] = field(default_factory=lambda: list(DEFAULT_QUERIES))
    relevance_keywords: List[str] = field(default_factory=lambda: list(DEFAULT_QUERIES))
    min_relevance: float = 0.05
    max_age_days: int = 365
    request_timeout: int = 25

    @classmethod
    def from_json(cls, path: str) -> "Config":
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return cls(
            brain_path=data.get("brain_path", DEFAULT_BRAIN),
            arxiv_categories=data.get("arxiv_categories", list(ARXIV_CATEGORIES)),
            domain_sources=data.get("domain_sources", list(DOMAIN_SOURCES)),
            search_queries=data.get("search_queries", list(DEFAULT_QUERIES)),
            relevance_keywords=data.get("relevance_keywords", list(DEFAULT_QUERIES)),
            min_relevance=float(data.get("min_relevance", 0.05)),
            max_age_days=int(data.get("max_age_days", 365)),
            request_timeout=int(data.get("request_timeout", 25)),
        )


def _http_get(url: str, timeout: int, headers: Optional[Dict[str, str]] = None) -> Optional[bytes]:
    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, text/html, application/xhtml+xml, */*",
    }
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, headers=request_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        log.warning("HTTP %s for %s: %s", exc.code, url, exc.reason)
    except urllib.error.URLError as exc:
        log.warning("Network error for %s: %s", url, exc.reason)
    except Exception as exc:
        log.warning("Fetch error for %s: %s", url, exc)
    return None


class Fetcher:
    def fetch(self, config: Config) -> List[Entry]:
        raise NotImplementedError


class ArxivRssFetcher(Fetcher):
    def fetch(self, config: Config) -> List[Entry]:
        entries: List[Entry] = []
        for category in config.arxiv_categories:
            url = f"https://export.arxiv.org/rss/{category}"
            raw = _http_get(url, config.request_timeout, headers={"Accept": "application/rss+xml"})
            if not raw:
                continue
            try:
                root = ET.fromstring(raw)
            except ET.ParseError as exc:
                log.warning("ArXiv RSS parse error for %s: %s", category, exc)
                continue
            for item in root.findall(".//item"):
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                desc_el = item.find("description")
                title = _clean_text(title_el.text if title_el is not None else "")
                link = _clean_text(link_el.text if link_el is not None else "")
                if not link:
                    continue
                pub = _clean_text(pub_el.text if pub_el is not None else datetime.date.today().isoformat())
                desc = _clean_text(desc_el.text if desc_el is not None else "")
                abstract = re.sub(r"^arXiv:\S+\s*", "", desc).strip()
                entries.append(
                    Entry(
                        title=title or link,
                        authors="-",
                        date=_iso_date(pub),
                        url=link,
                        abstract=abstract,
                        source=f"arXiv:{category}",
                        source_type="arxiv",
                    )
                )
        return entries


class DomainPageFetcher(Fetcher):
    def fetch(self, config: Config) -> List[Entry]:
        entries: List[Entry] = []
        crawler = _try_crawl4ai()
        for src in config.domain_sources:
            name = src.get("name", urlparse(src["url"]).netloc)
            url = src["url"]
            try:
                if crawler is not None:
                    result = crawler.run(url=url)
                    text = getattr(result, "markdown", "") or ""
                    title = _extract_title(text) or name
                    snippet = text[:600].strip()
                else:
                    raw = _http_get(url, config.request_timeout)
                    if raw is None:
                        continue
                    text = raw.decode("utf-8", errors="replace")
                    title = _extract_title(text) or name
                    snippet = _html_to_text(text)[:600].strip()
                entries.append(
                    Entry(
                        title=f"{name} — {title}",
                        authors="-",
                        date=datetime.date.today().isoformat(),
                        url=url,
                        abstract=snippet,
                        source=name,
                        source_type="domain",
                    )
                )
            except Exception as exc:
                log.warning("Domain fetch error for %s: %s", url, exc)
        return entries


class WebSearchFetcher(Fetcher):
    """API-key search backend."""


class SerpApiFetcher(WebSearchFetcher):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def fetch(self, config: Config) -> List[Entry]:
        entries: List[Entry] = []
        for query in config.search_queries:
            url = (
                "https://serpapi.com/search.json?"
                f"engine=google&q={quote_plus(query)}&api_key={self.api_key}&num=5"
            )
            raw = _http_get(url, config.request_timeout)
            if raw is None:
                continue
            try:
                data = json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError as exc:
                log.warning("SerpApi JSON error: %s", exc)
                continue
            for result in data.get("organic_results", []):
                link = result.get("link", "")
                if not link:
                    continue
                entries.append(
                    Entry(
                        title=_clean_text(result.get("title", link)),
                        authors="-",
                        date=datetime.date.today().isoformat(),
                        url=link,
                        abstract=_clean_text(result.get("snippet", "")),
                        source="SerpApi",
                        source_type="websearch",
                    )
                )
        return entries


class BingFetcher(WebSearchFetcher):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def fetch(self, config: Config) -> List[Entry]:
        entries: List[Entry] = []
        for query in config.search_queries:
            url = (
                "https://api.bing.microsoft.com/v7.0/search?"
                f"q={quote_plus(query)}&count=5"
            )
            raw = _http_get(url, config.request_timeout, headers={"Ocp-Apim-Subscription-Key": self.api_key})
            if raw is None:
                continue
            try:
                data = json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError as exc:
                log.warning("Bing JSON error: %s", exc)
                continue
            for result in data.get("webPages", {}).get("value", []):
                link = result.get("url", "")
                if not link:
                    continue
                entries.append(
                    Entry(
                        title=_clean_text(result.get("name", link)),
                        authors="-",
                        date=datetime.date.today().isoformat(),
                        url=link,
                        abstract=_clean_text(result.get("snippet", "")),
                        source="Bing",
                        source_type="websearch",
                    )
                )
        return entries


def _try_crawl4ai() -> Optional[object]:
    try:
        from crawl4ai import WebCrawler  # type: ignore
        crawler = WebCrawler()
        crawler.warmup()
        return crawler
    except Exception as exc:
        log.debug("crawl4ai unavailable: %s", exc)
        return None


def _clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_title(html_text: str) -> Optional[str]:
    match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if match:
        return _clean_text(match.group(1))
    return None


def _html_to_text(html_text: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return _clean_text(text)


def _iso_date(value: str) -> str:
    value = value.strip()
    if not value:
        return datetime.date.today().isoformat()
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%d",
        "%d %b %Y",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            return datetime.datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    match = re.search(r"(19|20)\d{2}", value)
    if match:
        return f"{match.group(0)}-01-01"
    return datetime.date.today().isoformat()


def _parse_age_days(date_str: str) -> int:
    try:
        d = datetime.date.fromisoformat(date_str)
    except ValueError:
        return 0
    return (datetime.date.today() - d).days


def relevance_score(entry: Entry, keywords: List[str]) -> Tuple[float, str]:
    blob = f"{entry.title} {entry.abstract}".lower()
    hits = 0.0
    matched: List[str] = []
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in blob:
            hits += 1.0
            matched.append(kw)
        else:
            tokens = [t for t in kw_lower.split() if len(t) > 2]
            token_hits = sum(1 for t in tokens if t in blob)
            if tokens:
                hits += 0.3 * token_hits / len(tokens)
                if token_hits:
                    matched.append(kw)
    denom = max(1, len(keywords))
    keyword_score = min(1.0, hits / denom)
    age = _parse_age_days(entry.date)
    recency_bonus = max(0.0, min(0.2, 0.2 - (age / 365.0) * 0.2))
    score = round(min(1.0, keyword_score + (recency_bonus if keyword_score > 0 else 0.0)), 3)
    return score, ", ".join(sorted(set(matched))) or "-"


class KnowledgeBrain:
    def __init__(self, path: str):
        self.path = path
        self.text = ""
        self.seen: set = set()
        self._load()

    def _load(self):
        if not os.path.exists(self.path):
            log.warning("Brain file not found at %s", self.path)
            self.text = ""
            return
        with open(self.path, "r", encoding="utf-8") as f:
            self.text = f.read()
        self.seen = set(re.findall(r"<!--hash:([0-9a-f]{16})-->", self.text))

    def append(
        self,
        entries: List[Entry],
        keywords: List[str],
        min_relevance: float,
        max_age_days: int = 365,
        dry_run: bool = False,
    ) -> int:
        today = datetime.date.today().isoformat()
        lines: List[str] = []
        added = 0
        for entry in entries:
            fp = entry.fingerprint()
            if fp in self.seen:
                log.debug("Skipping duplicate %s", entry.url)
                continue
            age = _parse_age_days(entry.date)
            if age > max_age_days:
                continue
            score, matched = relevance_score(entry, keywords)
            if score < min_relevance:
                continue
            self.seen.add(fp)
            lines.append(
                f"\n### [{today}] {_clean_text(entry.title)}\n"
                f"- Authors: {_clean_text(entry.authors) or '-'}\n"
                f"- Source: {_clean_text(entry.source)} ({_clean_text(entry.source_type)})\n"
                f"- Venue/URL: <{_clean_text(entry.url)}>\n"
                f"- Date: {_clean_text(entry.date)}\n"
                f"- Key finding: {_clean_text(entry.abstract)[:300]}\n"
                f"- Relevance score: {score}\n"
                f"- Matched keywords: {matched}\n"
                f"<!--hash:{fp}-->\n"
            )
            added += 1
        if added:
            block = f"\n<!-- crawl {today}: +{added} entries -->\n" + "".join(lines)
            if dry_run:
                log.info("DRY-RUN would append %d entries to %s", added, self.path)
                log.info(block[:800])
            else:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(block)
                log.info("Appended %d new entries to %s", added, self.path)
        else:
            log.info("No new relevant entries to append.")
        return added


def build_fetchers(config: Config) -> List[Fetcher]:
    fetchers: List[Fetcher] = [ArxivRssFetcher(), DomainPageFetcher()]
    serp_key = os.environ.get("SERPAPI_API_KEY")
    bing_key = os.environ.get("BING_SEARCH_API_KEY")
    if serp_key:
        fetchers.append(SerpApiFetcher(serp_key))
        log.info("Using SerpApi web search backend.")
    elif bing_key:
        fetchers.append(BingFetcher(bing_key))
        log.info("Using Bing web search backend.")
    else:
        log.info("No WebSearch API key configured; skipping live web search.")
    return fetchers


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Update SECOND-KNOWLEDGE-BRAIN.md for art-antique-valuation"
    )
    parser.add_argument("--brain", default=DEFAULT_BRAIN, help="Path to the knowledge brain markdown file")
    parser.add_argument("--config", help="Path to a JSON config file")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and score but do not write to the brain")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    if args.config:
        config = Config.from_json(args.config)
    else:
        config = Config(brain_path=os.path.abspath(args.brain))

    brain = KnowledgeBrain(config.brain_path)
    fetchers = build_fetchers(config)

    all_entries: List[Entry] = []
    for fetcher in fetchers:
        try:
            entries = fetcher.fetch(config)
            log.info("%s returned %d entries", type(fetcher).__name__, len(entries))
            all_entries.extend(entries)
        except Exception as exc:
            log.warning("Fetcher %s failed: %s", type(fetcher).__name__, exc)

    seen_run: set = set()
    unique_entries: List[Entry] = []
    for entry in all_entries:
        fp = entry.fingerprint()
        if fp not in seen_run:
            seen_run.add(fp)
            unique_entries.append(entry)

    added = brain.append(
        unique_entries,
        keywords=config.relevance_keywords,
        min_relevance=config.min_relevance,
        max_age_days=config.max_age_days,
        dry_run=args.dry_run,
    )
    log.info(
        "Knowledge updater finished. Fetched %d unique entries; added %d.",
        len(unique_entries),
        added,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
