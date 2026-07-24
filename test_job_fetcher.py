import json

import pytest

from job_fetcher import MARKER, _extract_json_object, build_search_url


def test_extract_json_object_basic():
    payload = {"data": {"jobs": [{"jobId": "R-414070", "title": "Data Engineer"}]}}
    html = (
        "<html><body><script>window.__STATE__="
        f'{{"eagerLoadRefineSearch":{json.dumps(payload)}, "other": 1}}'
        "</script></body></html>"
    )
    extracted = _extract_json_object(html, MARKER)
    assert json.loads(extracted) == payload


def test_extract_json_object_with_nested_braces_and_strings():
    payload = {
        "data": {
            "jobs": [
                {
                    "jobId": "R-1",
                    "title": 'Data Scientist, "AI} Team"',
                    "location": {"city": "Louisville", "state": "KY"},
                }
            ]
        }
    }
    html = f'blah blah {{"eagerLoadRefineSearch":{json.dumps(payload)}}} trailing junk'
    extracted = _extract_json_object(html, MARKER)
    assert json.loads(extracted) == payload


def test_extract_json_object_missing_marker_raises():
    with pytest.raises(ValueError):
        _extract_json_object("<html><body>no data here</body></html>", MARKER)


def test_extract_json_object_unbalanced_raises():
    html = '"eagerLoadRefineSearch":{"data": {"jobs": ['
    with pytest.raises(ValueError):
        _extract_json_object(html, MARKER)


def test_build_search_url():
    url = build_search_url("https://careers.humana.com/us/en/c/technology-and-digital-analytics-jobs", 200)
    assert url == "https://careers.humana.com/us/en/c/technology-and-digital-analytics-jobs?size=200&from=0"
