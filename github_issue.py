"""
Bonus feature: create a GitHub Issue per matched job so the user can "close"
it once they've decided whether to ask for a referral. Only jobs whose issue
is still OPEN get included in the email digest.

Uses the repo's built-in GITHUB_TOKEN (available for free in Actions) --
no extra secret needed for this part.
"""

import re

import requests

API_BASE = "https://api.github.com"


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def create_issue(repo, token, job, label="job-alert"):
    """Create a GitHub issue for `job` in `repo` (format: 'owner/name')."""
    url = f"{API_BASE}/repos/{repo}/issues"
    title = f"[Job] {job.get('title', 'Unknown title')} ({job.get('jobId', '')})"
    body = (
        f"**Title:** {job.get('title', '')}\n"
        f"**Req:** {job.get('jobId', '')}\n"
        f"**Location:** {job.get('location', '')}\n"
        f"**Posted:** {job.get('postedDate', '')}\n"
        f"**Apply:** {job.get('applyUrl', '')}\n\n"
        f"Close this issue once you've decided whether to pursue a referral."
    )
    response = requests.post(
        url,
        json={"title": title, "body": body, "labels": [label]},
        headers=_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def list_open_job_issues(repo, token, label="job-alert"):
    """Return {jobId: issue} for open issues labeled `label`, parsed out of
    the '(...)' suffix in the issue title created by create_issue()."""
    url = f"{API_BASE}/repos/{repo}/issues"
    issues = {}
    page = 1
    while True:
        response = requests.get(
            url,
            params={"state": "open", "labels": label, "per_page": 100, "page": page},
            headers=_headers(token),
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        for issue in batch:
            match = re.search(r"\(([^)]+)\)\s*$", issue["title"])
            if match:
                issues[match.group(1)] = issue
        if len(batch) < 100:
            break
        page += 1
    return issues
