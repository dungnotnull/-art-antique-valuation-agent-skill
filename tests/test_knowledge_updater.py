"""Unit tests for tools/knowledge_updater.py.

Run with: python -m pytest tests/test_knowledge_updater.py -v
"""
import os
import sys
from datetime import date
from pathlib import Path

import pytest

# Make the tools directory importable as a plain module namespace.
TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import knowledge_updater as ku


class TestEntry:
    def test_fingerprint_is_stable_and_url_sensitive(self):
        e1 = ku.Entry(title="Art Market Report", authors="A", date="2026-01-01", url="https://example.com/1",
                      abstract="Abstract A")
        e2 = ku.Entry(title="Art Market Report", authors="A", date="2026-01-01", url="https://example.com/2",
                      abstract="Abstract A")
        assert e1.fingerprint() == e1.fingerprint()
        assert e1.fingerprint() != e2.fingerprint()
        assert len(e1.fingerprint()) == 16


class TestCleanText:
    def test_strips_tags_and_entities(self):
        # Angle brackets are treated as HTML tags by the stripper, so <report> is removed.
        raw = "<p>Art &amp; Auctions:  &lt;report&gt; </p>"
        assert ku._clean_text(raw) == "Art & Auctions:"

    def test_collapses_whitespace(self):
        assert ku._clean_text("  a\n\tb ") == "a b"

    def test_handles_none(self):
        assert ku._clean_text(None) == ""


class TestIsoDate:
    def test_rss_format(self):
        assert ku._iso_date("Mon, 05 Jan 2026 00:00:00 GMT") == "2026-01-05"

    def test_iso_format(self):
        assert ku._iso_date("2026-06-22") == "2026-06-22"

    def test_fallback_year(self):
        assert ku._iso_date("Published in 2025 by Elsevier") == "2025-01-01"


class TestRelevanceScore:
    def test_exact_keyword_match(self):
        e = ku.Entry(title="Auction price index fine art 2026", authors="-", date="2026-01-01",
                     url="https://example.com", abstract="")
        score, matched = ku.relevance_score(e, ku.DEFAULT_QUERIES)
        assert 0 < score <= 1.0
        assert "auction price index fine art 2026" in matched

    def test_old_entry_gets_lower_score(self):
        old = ku.Entry(title="Auction price index fine art 2026", authors="-", date="2020-01-01",
                       url="https://example.com", abstract="")
        new = ku.Entry(title="Auction price index fine art 2026", authors="-", date=date.today().isoformat(),
                       url="https://example.com/2", abstract="")
        s_old, _ = ku.relevance_score(old, ku.DEFAULT_QUERIES)
        s_new, _ = ku.relevance_score(new, ku.DEFAULT_QUERIES)
        assert s_new > s_old

    def test_irrelevant_entry_scores_zero(self):
        e = ku.Entry(title="Unrelated cooking recipe", authors="-", date=date.today().isoformat(),
                     url="https://example.com", abstract="")
        score, matched = ku.relevance_score(e, ku.DEFAULT_QUERIES)
        assert score == 0.0
        assert matched == "-"


class TestKnowledgeBrain:
    def test_loads_existing_hashes(self, tmp_path):
        brain_path = tmp_path / "brain.md"
        brain_path.write_text("# Brain\n### old\n<!--hash:aaaaaaaaaaaaaaaa-->\n", encoding="utf-8")
        brain = ku.KnowledgeBrain(str(brain_path))
        assert "aaaaaaaaaaaaaaaa" in brain.seen

    def test_appends_new_entries(self, tmp_path):
        brain_path = tmp_path / "brain.md"
        brain_path.write_text("# Brain\n", encoding="utf-8")
        brain = ku.KnowledgeBrain(str(brain_path))
        entries = [
            ku.Entry(title="Auction price index fine art 2026", authors="-", date=date.today().isoformat(),
                     url="https://example.com/1", abstract="Market liquidity trend."),
        ]
        added = brain.append(entries, ku.DEFAULT_QUERIES, min_relevance=0.05, dry_run=False)
        assert added == 1
        content = brain_path.read_text(encoding="utf-8")
        assert "Auction price index fine art 2026" in content
        assert "hash:" in content

    def test_dedup_skips_duplicate_on_second_append(self, tmp_path):
        brain_path = tmp_path / "brain.md"
        brain_path.write_text("# Brain\n", encoding="utf-8")
        brain = ku.KnowledgeBrain(str(brain_path))
        e = ku.Entry(title="Auction price index fine art 2026", authors="-", date=date.today().isoformat(),
                     url="https://example.com/1", abstract="Market liquidity trend.")
        added1 = brain.append([e], ku.DEFAULT_QUERIES, min_relevance=0.05, dry_run=False)
        added2 = brain.append([e], ku.DEFAULT_QUERIES, min_relevance=0.05, dry_run=False)
        assert added1 == 1
        assert added2 == 0


class TestArxivRssFetcher:
    SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Market Liquidity and Art Prices</title>
          <link>https://arxiv.org/abs/2601.00001</link>
          <pubDate>Mon, 05 Jan 2026 00:00:00 GMT</pubDate>
          <description>arXiv:2601.00001 Abstract here.</description>
        </item>
      </channel>
    </rss>"""

    def test_parses_feed(self, monkeypatch):
        def fake_http_get(url, timeout, headers=None):
            if "econ.GN" in url:
                return self.SAMPLE_RSS.encode("utf-8")
            return None

        monkeypatch.setattr(ku, "_http_get", fake_http_get)
        fetcher = ku.ArxivRssFetcher()
        entries = fetcher.fetch(ku.Config())
        assert len(entries) == 1
        assert entries[0].title == "Market Liquidity and Art Prices"
        assert entries[0].url == "https://arxiv.org/abs/2601.00001"
        assert entries[0].date == "2026-01-05"
        assert "arXiv:" not in entries[0].abstract


class TestDomainPageFetcher:
    def test_falls_back_to_urllib(self, monkeypatch):
        html = "<html><head><title>Heritage Auctions Results</title></head><body>Lots of results.</body></html>"

        def fake_http_get(url, timeout, headers=None):
            return html.encode("utf-8")

        monkeypatch.setattr(ku, "_http_get", fake_http_get)
        monkeypatch.setattr(ku, "_try_crawl4ai", lambda: None)

        fetcher = ku.DomainPageFetcher()
        entries = fetcher.fetch(ku.Config())
        assert len(entries) == len(ku.DOMAIN_SOURCES)
        heritage = next(e for e in entries if "Heritage" in e.title)
        assert "Heritage Auctions Results" in heritage.title
        assert "Lots of results" in heritage.abstract


class TestBuildFetchers:
    def test_without_keys_returns_two_fetchers(self, monkeypatch):
        monkeypatch.delenv("SERPAPI_API_KEY", raising=False)
        monkeypatch.delenv("BING_SEARCH_API_KEY", raising=False)
        fetchers = ku.build_fetchers(ku.Config())
        names = [type(f).__name__ for f in fetchers]
        assert names == ["ArxivRssFetcher", "DomainPageFetcher"]

    def test_with_serpapi_returns_three_fetchers(self, monkeypatch):
        monkeypatch.setenv("SERPAPI_API_KEY", "test_key")
        monkeypatch.delenv("BING_SEARCH_API_KEY", raising=False)
        fetchers = ku.build_fetchers(ku.Config())
        names = [type(f).__name__ for f in fetchers]
        assert "SerpApiFetcher" in names


class TestConfig:
    def test_from_json(self, tmp_path):
        cfg_path = tmp_path / "cfg.json"
        cfg_path.write_text("""{
            "min_relevance": 0.2,
            "max_age_days": 180,
            "request_timeout": 10,
            "search_queries": ["new query"]
        }""", encoding="utf-8")
        cfg = ku.Config.from_json(str(cfg_path))
        assert cfg.min_relevance == 0.2
        assert cfg.max_age_days == 180
        assert cfg.request_timeout == 10
        assert cfg.search_queries == ["new query"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
