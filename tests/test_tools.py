import json
from pathlib import Path

import dspy
import pytest

from dspy_contextfetch import read_page, web_search

KEY_FILE = Path.home() / ".contextfetch_smoke_key"


@pytest.fixture
def mocked(monkeypatch):
    monkeypatch.setenv("CONTEXTFETCH_API_KEY", "k")
    # The contextfetch SDK calls urllib.request.urlopen; record each request and answer it.
    api = {"calls": [], "search": {"results": []}}

    class Res:
        def __init__(self, body, headers=None):
            self.body, self.headers = body, headers or {}

        def read(self):
            return self.body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout):
        api["calls"].append(req)
        if req.full_url.endswith("/v1/search"):
            return Res(json.dumps(api["search"]).encode())
        return Res(b"# Page")

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    return api


def test_web_search(mocked):
    mocked["search"] = {"results": [{"title": "T", "url": "https://a.dev", "prunedContext": "body"}]}
    out = web_search("q", num_results=3, include_domains=["a.dev"])
    body = json.loads(mocked["calls"][0].data)
    assert body == {
        "query": "q",
        "numResults": 3,
        "includeDomains": ["a.dev"],
        "contents": {"pruned_context": True},
    }
    assert mocked["calls"][0].headers["Authorization"] == "Bearer k"
    assert out == "Title: T\nURL: https://a.dev\nPublished: unknown\n\nbody"


def test_web_search_empty(mocked):
    assert web_search("q") == "No results found."


def test_read_page(mocked):
    assert read_page("https://a.dev/x", query="what") == "# Page"
    assert mocked["calls"][0].full_url == "https://api.contextfetch.dev/r/https://a.dev/x?q=what"


def test_dspy_tool_schema():
    tool = dspy.Tool(web_search)
    assert tool.name == "web_search"
    assert set(tool.args) == {"query", "num_results", "include_domains", "start_published_date"}
    assert dspy.Tool(read_page).args["url"] == {"type": "string"}


@pytest.mark.skipif(not KEY_FILE.exists(), reason="no live key")
def test_live(monkeypatch):
    monkeypatch.setenv("CONTEXTFETCH_API_KEY", KEY_FILE.read_text().strip())
    assert "URL: https://" in web_search("python asyncio TaskGroup", num_results=2)
    assert "TaskGroup" in read_page("https://docs.python.org/3/library/asyncio-task.html", "TaskGroup")
