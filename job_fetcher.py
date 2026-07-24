"""
Fetches Humana's category page and pulls the server-rendered
"eagerLoadRefineSearch" JSON blob out of the raw HTML.

No headless browser, no BeautifulSoup -- just requests + a hand-rolled
brace-matcher + json.loads. Phenom (the vendor behind careers.humana.com)
embeds a JSON object literal right in the HTML; we find the marker string
and walk forward counting braces (respecting quoted strings) until they
balance back to zero.
"""

import json

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

MARKER = '"eagerLoadRefineSearch":{'


def _extract_json_object(html, marker):
    """Find `marker` in `html` and brace-match from its trailing '{' to
    return the full JSON object substring (inclusive of both braces)."""
    start = html.find(marker)
    if start == -1:
        raise ValueError(f"Marker {marker!r} not found in page HTML")

    brace_start = start + len(marker) - 1  # index of the opening '{'
    depth = 0
    in_string = False
    escape = False

    i = brace_start
    while i < len(html):
        ch = html[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return html[brace_start : i + 1]
        i += 1

    raise ValueError("Unbalanced braces while extracting JSON object")


def fetch_jobs(url, timeout=30):
    """Fetch `url`, extract eagerLoadRefineSearch, and return data.jobs[]."""
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    raw_json = _extract_json_object(response.text, MARKER)
    parsed = json.loads(raw_json)
    return parsed.get("data", {}).get("jobs", [])


def build_search_url(category_url, page_size):
    return f"{category_url}?size={page_size}&from=0"
