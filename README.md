# dspy-contextfetch

[ContextFetch](https://contextfetch.dev) web search and page reading as [DSPy](https://dspy.ai) tools.

```bash
pip install dspy-contextfetch
export CONTEXTFETCH_API_KEY="..."   # optional: without a key, requests use the keyless tier
```

```python
import dspy
from dspy_contextfetch import read_page, web_search

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))
agent = dspy.ReAct("question -> answer", tools=[web_search, read_page])
print(agent(question="What does asyncio.TaskGroup do when a task fails?").answer)
```

- `web_search(query, num_results=5, include_domains=None, start_published_date=None)`: the top results as
  Markdown, each with title, URL, published date and the parts of the page relevant to the query.
- `read_page(url, query=None)`: one page as Markdown; with `query`, only the parts relevant to it.

Both are plain functions over the [`contextfetch`](https://pypi.org/project/contextfetch/) SDK, so they also
work with `dspy.Tool(...)` or called directly. Errors from the API raise `contextfetch.ContextFetchError`.

## Tests

```bash
uv run --group test pytest
```

The live test runs when `~/.contextfetch_smoke_key` exists.
