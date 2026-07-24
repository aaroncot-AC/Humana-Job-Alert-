"""
Config for the Humana job-alert bot.

Edit INCLUDE_KEYWORDS / EXCLUDE_KEYWORDS to change what counts as a match.
Matching is done against a NORMALIZED title (lowercased, commas stripped,
whitespace collapsed) -- see title_matcher.py.
"""

# Humana's "Technology and Digital Analytics" job category page.
CATEGORY_URL = "https://careers.humana.com/us/en/c/technology-and-digital-analytics-jobs"
PAGE_SIZE = 200

# Title must contain AT LEAST ONE of these (case-insensitive, substring match).
INCLUDE_KEYWORDS = [
    "data engineer",
    "data scientist",
    "business intelligence",
    "bi engineer",
    "informaticist",
]

# Title must contain NONE of these (case-insensitive, substring match).
EXCLUDE_KEYWORDS = [
    "director",
    "vp",
    "vice president",
    "principal",
    "manager",
    "lead",
    "head of",
    "intern",
]

# The "database" -- a JSON file of jobIds we've already shown the user,
# committed back to the repo by the GitHub Actions workflow each run.
SEEN_JOBS_FILE = "seen_jobs.json"

# Label applied to GitHub Issues created for matches (bonus feature).
GITHUB_ISSUE_LABEL = "job-alert"
