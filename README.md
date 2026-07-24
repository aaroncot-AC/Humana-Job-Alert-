# Humana Job Alert Bot

Checks Humana's "Technology and Digital Analytics" job category, filters by
title, and emails you (only you) a digest of new matches. Runs on GitHub
Actions for free, twice a day.

## Files

- `config.py` — include/exclude title keywords, category URL. Edit this to
  change what counts as a match.
- `title_matcher.py` — normalizes and matches titles.
- `job_fetcher.py` — fetches the Humana category page and extracts the
  `eagerLoadRefineSearch` JSON blob via brace-matching (no headless browser).
- `email_digest.py` — builds and sends the digest email via Resend.
- `github_issue.py` — bonus: creates a GitHub Issue per match; only jobs
  with a still-open issue get emailed.
- `main.py` — wires it all together; entry point.
- `seen_jobs.json` — the "database" of jobIds already shown to you. Committed
  back to the repo by the workflow each run.
- `.github/workflows/job-alert.yml` — cron schedule + manual trigger.
- `test_title_matcher.py`, `test_job_fetcher.py` — pytest unit tests.

## Setup

### 1. Sign up for Resend

1. Go to resend.com and create a free account.
2. Once logged in, go to **API Keys** and create a new key (full access is
   fine). Copy it — you'll paste it into a GitHub secret below.
3. You do **not** need to verify a domain. The bot sends from
   `onboarding@resend.dev`, Resend's shared test address, which works
   out of the box on the free tier as long as the **To** address is the
   same email you used to sign up for Resend (Resend's free tier only
   delivers to your own verified account email unless you verify a custom
   domain). Make sure `DIGEST_TO_EMAIL` (below) matches your Resend account
   email, or verify a domain in Resend if you want to send elsewhere.

### 2. Create a GitHub repo and push this code

Create a new repo (can be private) and push these files to it as-is.

### 3. Add GitHub secrets

In the repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add:

| Secret name | Value |
|---|---|
| `DIGEST_TO_EMAIL` | Your email address (must match your Resend account email unless you've verified a domain) |
| `RESEND_API_KEY` | The API key from step 1 |
| `FROM_EMAIL` | Optional. Leave unset to default to `onboarding@resend.dev`, or set it if you've verified your own domain in Resend |

You do **not** need to add a `GITHUB_TOKEN` secret — Actions provides one
automatically, and the workflow already grants it `contents: write` and
`issues: write` permissions for committing `seen_jobs.json` and creating
issues.

### 4. First run

Go to the **Actions** tab in your repo → **Humana Job Alert** → **Run
workflow** → Run workflow. This does a manual run without waiting for the
cron schedule.

On the first run, everything currently posted that matches your filters will
be new (since `seen_jobs.json` starts empty), so expect a bigger first
digest and a batch of GitHub issues if you left issue creation on. After
that, you'll only hear about genuinely new postings.

### 5. Ongoing

It now runs automatically at ~9am and ~4pm US Eastern, plus whenever you
trigger it manually. Each run commits an updated `seen_jobs.json` back to
the repo, so dedup persists across runs without any external database.

To adjust who's excluded/included, edit `INCLUDE_KEYWORDS` /
`EXCLUDE_KEYWORDS` in `config.py` and push — no other changes needed.

## Local testing (optional)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in DIGEST_TO_EMAIL and RESEND_API_KEY
pytest -q
python main.py
```
