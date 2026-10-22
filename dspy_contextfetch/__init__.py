"""ContextFetch web search and page reading as DSPy tools.

Plain functions, so they work anywhere DSPy takes a tool: `dspy.ReAct(sig, tools=[web_search, read_page])`
or `dspy.Tool(web_search)`. The API key comes from the CONTEXTFETCH_API_KEY environment variable; without
one, requests use the keyless tier.
"""

from __future__ import annotations

from contextfetch import ContextFetch

__all__ = ["read_page", "web_search"]


def web_search(
    query: str,
    num_results: int = 5,
    include_domains: list[str] | None = None,
    start_published_date: str | None = None,
) -> str:
    """Search the web. Returns the top results as Markdown: title, URL, published date and the parts of
    each page relevant to the query. num_results is 1 to 25; include_domains limits results to those
    domains; start_published_date (YYYY-MM-DD) keeps only pages published on or after that date."""
    response = ContextFetch().search(
        query,
        num_results=num_results,
        include_domains=include_domains,
        start_published_date=start_published_date,
        pruned_context=True,
    )
    results = response.get("results") or []
    if not results:
        return "No results found."
    return "\n\n---\n\n".join(
        f"Title: {r.get('title') or ''}\n"
        f"URL: {r.get('url', '')}\n"
        f"Published: {r.get('publishedDate') or 'unknown'}\n\n"
        f"{r.get('prunedContext') or ''}"
        for r in results
    )


def read_page(url: str, query: str | None = None) -> str:
    """Read a web page and return its content as Markdown. With query, return only the parts of the page
    relevant to that question."""
    return ContextFetch().read(url, query=query).markdown
