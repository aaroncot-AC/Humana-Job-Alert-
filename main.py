"""
Orchestrator: fetch Humana jobs -> filter by title -> dedup against
seen_jobs.json -> (optionally) create GitHub Issues -> email a digest of
new matches to DIGEST_TO_EMAIL only.

Run manually with a local .env (see .env.example), or via the GitHub
Actions workflow in .github/workflows/job-alert.yml.

GOTCHA: GitHub Actions turns UNSET secrets into EMPTY STRINGS, not missing
env vars. Every optional env var below is read with
    os.environ.get("X", "").strip() or "the-default"
NOT os.environ.get("X", "the-default") -- the latter lets "" slip through
silently (e.g. Resend rejects an empty From address with a 422).
"""

import json
import os
import sys

from dotenv import load_dotenv

import config
import github_issue
from email_digest import send_digest
from job_fetcher import build_search_url, fetch_jobs
from title_matcher import title_matches

load_dotenv()  # no-op in CI; convenient for local runs with a .env file


def load_seen_jobs(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_seen_jobs(path, seen_jobs):
    with open(path, "w") as f:
        json.dump(seen_jobs, f, indent=2, sort_keys=True)
        f.write("\n")


def main():
    to_email = os.environ.get("DIGEST_TO_EMAIL", "").strip()
    resend_api_key = os.environ.get("RESEND_API_KEY", "").strip()
    # Correct pattern per the gotcha above: "" must fall through to the default.
    from_email = os.environ.get("FROM_EMAIL", "").strip() or "onboarding@resend.dev"
    github_token = os.environ.get("GITHUB_TOKEN", "").strip()
    github_repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    create_issues = os.environ.get("CREATE_GITHUB_ISSUES", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )

    if not to_email:
        print("DIGEST_TO_EMAIL is not set; refusing to run.", file=sys.stderr)
        sys.exit(1)
    if not resend_api_key:
        print("RESEND_API_KEY is not set; refusing to run.", file=sys.stderr)
        sys.exit(1)

    seen_jobs = load_seen_jobs(config.SEEN_JOBS_FILE)

    search_url = build_search_url(config.CATEGORY_URL, config.PAGE_SIZE)
    all_jobs = fetch_jobs(search_url)
    print(f"Fetched {len(all_jobs)} total jobs from Humana.")

    matches = [
        job
        for job in all_jobs
        if title_matches(job.get("title", ""), config.INCLUDE_KEYWORDS, config.EXCLUDE_KEYWORDS)
    ]
    print(f"{len(matches)} jobs match the title filters.")

    new_matches = [job for job in matches if job.get("jobId") not in seen_jobs]
    print(f"{len(new_matches)} are new (not already in seen_jobs.json).")

    open_issue_job_ids = None
    if create_issues and github_token and github_repo:
        for job in new_matches:
            job_id = job.get("jobId")
            try:
                issue = github_issue.create_issue(
                    github_repo, github_token, job, label=config.GITHUB_ISSUE_LABEL
                )
                seen_jobs.setdefault(job_id, {})["issue_number"] = issue["number"]
                seen_jobs[job_id]["issue_url"] = issue["html_url"]
                print(f"Created issue #{issue['number']} for {job_id}.")
            except Exception as exc:  # noqa: BLE001 -- keep the run going
                print(f"Failed to create issue for {job_id}: {exc}", file=sys.stderr)

        try:
            open_issue_job_ids = set(
                github_issue.list_open_job_issues(
                    github_repo, github_token, label=config.GITHUB_ISSUE_LABEL
                ).keys()
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to list open issues: {exc}", file=sys.stderr)

    # Record every current match as seen, preserving any existing metadata
    # (e.g. issue_number) and first-seen date.
    for job in matches:
        job_id = job.get("jobId")
        entry = seen_jobs.get(job_id, {})
        entry.update(
            {
                "title": job.get("title"),
                "applyUrl": job.get("applyUrl"),
                "location": job.get("location"),
                "postedDate": job.get("postedDate"),
                "firstSeen": entry.get("firstSeen") or job.get("postedDate"),
            }
        )
        seen_jobs[job_id] = entry

    # Only email about jobs whose GitHub issue is still open, when issue
    # tracking is enabled.
    to_notify = new_matches
    if open_issue_job_ids is not None:
        to_notify = [job for job in to_notify if job.get("jobId") in open_issue_job_ids]

    if to_notify:
        send_digest(to_notify, to_email=to_email, from_email=from_email, api_key=resend_api_key)
        print(f"Sent digest email with {len(to_notify)} job(s) to {to_email}.")
    else:
        print("No new jobs to email.")

    save_seen_jobs(config.SEEN_JOBS_FILE, seen_jobs)


if __name__ == "__main__":
    main()
