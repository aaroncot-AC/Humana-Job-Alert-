"""
Title normalization and include/exclude matching.

Humana mixes styles like "Senior, Data Scientist" and "Senior Data Scientist"
in the same category page. normalize_title() makes both compare equal.
"""

import re


def normalize_title(title):
    """Lowercase, strip commas, and collapse whitespace."""
    if title is None:
        return ""
    normalized = title.lower()
    normalized = normalized.replace(",", "")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def title_matches(title, include_keywords, exclude_keywords):
    """True if the normalized title contains an include keyword and no
    exclude keyword."""
    normalized = normalize_title(title)
    if not any(keyword in normalized for keyword in include_keywords):
        return False
    if any(keyword in normalized for keyword in exclude_keywords):
        return False
    return True
