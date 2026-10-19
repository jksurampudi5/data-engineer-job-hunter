#!/usr/bin/env python3
"""Strict URL checker for Data Engineer job applications.

Ensures every listing has an active, reachable, direct application page
with an apply action and no expiration/closure signals.
"""

from __future__ import annotations
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "jobs.json"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

EXPIRY_PATTERNS = (
    r"job\s+(?:has\s+)?expired",
    r"position\s+(?:has\s+)?been\s+filled",
    r"position\s+is\s+filled",
    r"no\s+longer\s+(?:accepting\s+applications|available)",
    r"this\s+vacancy\s+has\s+now\s+expired",
    r"job\s+(?:is\s+)?not\s+available",
    r"not\s+currently\s+available",
    r"opportunity\s+is\s+closed",
    r"this\s+job\s+is\s+closed",
    r"we\s+couldn['’]t\s+find\s+that\s+page",
    r"page\s+not\s+found",
    r"404\s+not\s+found",
    r"application\s+error",
    r"502\s+bad\s+gateway",
)

APPLY_PATTERNS = (
    r"apply\s+(?:now|for\s+this\s+job|online)",
    r"submit\s+application",
    r"apply-button",
    r"post-form",
    r"job-apply",
    r"application-form",
    r"myworkdayjobs\.com",
    r"smartrecruiters\.com",
    r"greenhouse\.io",
    r"lever\.co",
)


def check_url(url: str, title: str = "") -> tuple[bool, int | None, str, str]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            final_url = response.geturl()
            status = response.status
            content = response.read(400_000).decode("utf-8", errors="ignore").lower()

        if status >= 400:
            return False, status, final_url, f"HTTP {status}"

        # Detect expiration / vacancy filled
        for pattern in EXPIRY_PATTERNS:
            if re.search(pattern, content):
                return False, status, final_url, f"expired pattern detected ({pattern})"

        # Detect category / search page trap without an actual apply form
        if "opportunities found" in content and "search jobs" in content:
            return False, status, final_url, "generic search results page detected without apply form"

        # Check for apply presence
        has_apply = any(re.search(pattern, content) for pattern in APPLY_PATTERNS)
        if not has_apply:
            return False, status, final_url, "no apply action found on page"

        return True, status, final_url, "direct apply page verified"

    except HTTPError as error:
        return False, error.code, error.geturl(), f"HTTP {error.code}"
    except (TimeoutError, URLError, OSError) as error:
        return False, None, url, type(error).__name__


def main() -> int:
    jobs = json.loads(DATA_FILE.read_text())
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    failures = 0

    print(f"Starting check of {len(jobs)} jobs at {now}...")
    for job in jobs:
        preferred = job.get("preferredUrl") or job.get("applicationUrl")
        ok, status, final_url, note = check_url(preferred, job.get("title", ""))

        job["applicationUrl"] = preferred
        job["finalUrl"] = final_url
        job["httpStatus"] = status
        job["lastCheckedAt"] = now
        job["linkCheckNote"] = note

        if ok:
            job["linkStatus"] = "verified"
            job["linkStatusLabel"] = "Direct apply"
            job["status"] = "apply"
            job["statusLabel"] = "Apply now"
            print(f"  ✓ {job['company']} — {job['title']} -> {note}")
        else:
            job["linkStatus"] = "needs-review"
            job["linkStatusLabel"] = "Unavailable"
            job["status"] = "monitor"
            job["statusLabel"] = "Needs review"
            failures += 1
            print(f"  ✗ {job['company']} — {job['title']} -> FAIL: {note}")

    DATA_FILE.write_text(json.dumps(jobs, indent=2, ensure_ascii=False) + "\n")
    print(f"\nCompleted: {len(jobs) - failures} verified active, {failures} failures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
