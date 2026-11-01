"""Pick roles, areas, and a timeline, then open every LinkedIn job search combo in the browser."""

import time
import webbrowser
from urllib.parse import urlencode

BASE_URL = "https://www.linkedin.com/jobs/search-results/?"

ROLES = [
    "IT entry level",
    "Software entry level",
    "Automation entry level",
    "Ai agent entry level",
    "Data science entry level",
]

AREAS = {
    "Dallas-Fort Worth Metroplex, TX": "90000031",
    "Nashville Metropolitan Area, TN": "90000536",
    "Metro Jacksonville, FL": "90000359",
    "Charlotte Metro, NC": "90000152",
    "Seattle metropolitan area, WA": "119319718",
    "Seattle, WA (city)": "104116203",
    "Minnesota (state)": "103411167",
    "Texas (state)": "102748797",
    "Tennessee (state)": "104629187",
    "Florida (state)": "101318387",
    "North Carolina (state)": "103255397",
    "Georgia (state)": "103950076",
    "Washington (state)": "103977389",
}

TIMELINES = {
    "1 day": "r86400",
    "2 days": "r172800",
    "3 days": "r259200",
    "4 days": "r345600",
    "5 days": "r432000",
    "1 week": "r604800",
}

TAB_LIMIT_WARNING = 15


def pick_many(title, options):
    """Show a numbered menu; accept '1,3,5', ranges like '2-4', or 'a' for all."""
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("Choose (e.g. 1,3 or 2-4, 'a' = all): ").strip().lower()
        if raw in ("a", "all"):
            return list(options)
        try:
            picks = set()
            for part in raw.split(","):
                part = part.strip()
                if "-" in part:
                    lo, hi = map(int, part.split("-"))
                    picks.update(range(lo, hi + 1))
                elif part:
                    picks.add(int(part))
            if picks and all(1 <= p <= len(options) for p in picks):
                return [options[p - 1] for p in sorted(picks)]
        except ValueError:
            pass
        print("  Invalid choice, try again.")


def pick_one(title, options):
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("Choose one: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("  Invalid choice, try again.")


def build_url(role, geo_id, tpr):
    params = {
        "keywords": role,
        "origin": "JOB_SEARCH_PAGE_JOB_FILTER",
        "geoId": geo_id,
        "f_TPR": tpr,
    }
    return BASE_URL + urlencode(params)


def main():
    roles = pick_many("Roles:", ROLES)
    areas = pick_many("Areas:", list(AREAS))
    timeline = pick_one("Posted within:", list(TIMELINES))

    urls = [
        (f"{role} | {area}", build_url(role, AREAS[area], TIMELINES[timeline]))
        for role in roles
        for area in areas
    ]

    print(f"\n{len(urls)} searches ({timeline}):")
    for label, _ in urls:
        print(f"  - {label}")

    if len(urls) > TAB_LIMIT_WARNING:
        if input(f"\nThat's {len(urls)} tabs. Open them all? (y/n): ").strip().lower() != "y":
            print("Cancelled.")
            return

    for _, url in urls:
        webbrowser.open_new_tab(url)
        time.sleep(0.5)  # small gap so the browser doesn't drop tabs

    print("\nDone. Good luck today!")


if __name__ == "__main__":
    main()
