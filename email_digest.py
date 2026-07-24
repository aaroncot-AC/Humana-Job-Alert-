"""
Builds and sends the one digest email per run via Resend's API.

Only ever sends to DIGEST_TO_EMAIL -- never to anyone else. The digest
includes one mailto: link with a pre-drafted referral request listing the
matched jobs; the To: line is left blank for the user to fill in.
"""

import urllib.parse

import requests

RESEND_API_URL = "https://api.resend.com/emails"


def build_mailto_link(jobs):
    subject = "Referral request: Humana roles"
    lines = [
        "Hi,",
        "",
        "I'm interested in a referral for the following Humana role(s) I found:",
        "",
    ]
    for job in jobs:
        lines.append(f"- {job.get('title', 'Unknown title')} (req {job.get('jobId', '')}) - {job.get('applyUrl', '')}")
    lines.append("")
    lines.append("Thanks!")
    body = "\n".join(lines)

    # No "to" param -- leave the To: line blank for the user to fill in.
    query = urllib.parse.urlencode({"subject": subject, "body": body})
    return f"mailto:?{query}"


def build_digest_html(jobs, mailto_link):
    if jobs:
        items = []
        for job in jobs:
            title = job.get("title", "Unknown title")
            job_id = job.get("jobId", "")
            apply_url = job.get("applyUrl", "")
            location = job.get("location", "")
            location_suffix = f" &mdash; {location}" if location else ""
            items.append(
                f'<li><a href="{apply_url}">{title}</a> '
                f"(req {job_id}){location_suffix}</li>"
            )
        jobs_html = "<ul>" + "\n".join(items) + "</ul>"
    else:
        jobs_html = "<p>No new matches.</p>"

    return f"""
    <div>
      <h2>Humana job alert &mdash; {len(jobs)} new match(es)</h2>
      {jobs_html}
      <p><a href="{mailto_link}">Draft a referral request email</a></p>
    </div>
    """.strip()


def build_digest_text(jobs, mailto_link):
    lines = [f"Humana job alert - {len(jobs)} new match(es)", ""]
    for job in jobs:
        lines.append(
            f"- {job.get('title', 'Unknown title')} (req {job.get('jobId', '')}): {job.get('applyUrl', '')}"
        )
    if not jobs:
        lines.append("No new matches.")
    lines.append("")
    lines.append(f"Draft a referral request email: {mailto_link}")
    return "\n".join(lines)


def send_digest(jobs, to_email, from_email, api_key):
    """Send one digest email listing `jobs` to `to_email` via Resend."""
    mailto_link = build_mailto_link(jobs)
    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": f"Humana job alert: {len(jobs)} new match(es)",
        "html": build_digest_html(jobs, mailto_link),
        "text": build_digest_text(jobs, mailto_link),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
