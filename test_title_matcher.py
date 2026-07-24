import pytest

from config import EXCLUDE_KEYWORDS, INCLUDE_KEYWORDS
from title_matcher import normalize_title, title_matches


def test_normalize_lowercases():
    assert normalize_title("Senior Data Scientist") == "senior data scientist"


def test_normalize_strips_commas():
    assert normalize_title("Senior, Data Scientist") == "senior data scientist"


def test_normalize_collapses_whitespace():
    assert normalize_title("Senior   Data    Scientist") == "senior data scientist"


def test_normalize_handles_none():
    assert normalize_title(None) == ""


def test_normalize_idempotent_on_mixed_styles():
    a = normalize_title("Senior, Data Scientist")
    b = normalize_title("Senior Data Scientist")
    assert a == b


@pytest.mark.parametrize(
    "title",
    [
        "Data Engineer II",
        "Senior Data Scientist",
        "Senior, Data Scientist",
        "Business Intelligence Analyst",
        "BI Engineer",
        "Informaticist",
        "Senior Informaticist, Digital Health",
        "Associate Data Engineer",
    ],
)
def test_matches_include_keywords(title):
    assert title_matches(title, INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS)


@pytest.mark.parametrize(
    "title",
    [
        "Director, Data Engineering",
        "VP, Business Intelligence",
        "Vice President of Data Science",
        "Principal Data Scientist",
        "Data Engineering Manager",
        "Lead Data Scientist",
        "Head of Business Intelligence",
        "Data Scientist Intern",
    ],
)
def test_excludes_seniority_and_intern_titles(title):
    assert not title_matches(title, INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS)


def test_no_include_keyword_means_no_match():
    assert not title_matches("Software Engineer", INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS)


def test_case_insensitivity():
    assert title_matches("DATA ENGINEER", INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS)


def test_empty_title_no_match():
    assert not title_matches("", INCLUDE_KEYWORDS, EXCLUDE_KEYWORDS)
