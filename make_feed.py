#!/usr/bin/env python3
"""Build the test feeds in docs/, one folder per step, from the real Picture Window feed.

Every step reuses the real feed's photo files (GitHub release URLs), so nothing big lives here: only
small index.json and manifest files. Each step has its own folder so a TV can move between them
without waiting for GitHub Pages' cache.

Usage: python3 make_feed.py                  # month-1, month-2, bad-month
       python3 make_feed.py remove <id>      # removal: month-2 with <id> removed
       python3 make_feed.py broken <id>      # broken-list: month-2 with September's list damaged and <id> removed
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

REAL_FEED = "https://corinnekunze.github.io/picture-window/"
DOCS = Path(__file__).parent / "docs"
FIRST_MONTH_SIZE = 700


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "picture-window-test-feed"})
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def real_photos():
    """The real feed's live photos, in its order, revoked ones left out."""
    index = fetch_json(REAL_FEED + "index.json")
    revoked = set(index["revoked"])
    photos = []
    for batch in index["batches"]:
        photos += [item for item in fetch_json(REAL_FEED + batch["manifest"])["items"] if item["id"] not in revoked]
    return photos


def write_step(step, batches, revoked=(), damaged=()):
    """Writes docs/<step>/: one manifest per batch and the index. [damaged] batches get the wrong hash."""
    folder = DOCS / step
    (folder / "batches").mkdir(parents=True, exist_ok=True)
    refs = []
    for batch_id, items in sorted(batches.items(), reverse=True):
        manifest = json.dumps({"schema": 1, "batch": batch_id, "published": "2026-10-25T00:00:00Z", "items": items}).encode()
        (folder / "batches" / f"{batch_id}.json").write_bytes(manifest)
        sha = hashlib.sha256(manifest).hexdigest()
        if batch_id in damaged:
            sha = "0" * 64
        refs.append({"id": batch_id, "manifest": f"batches/{batch_id}.json", "sha256": sha, "count": len(items)})
    index = {"schema": 1, "published": f"2026-10-25T00:00:00Z/{step}", "batches": refs, "revoked": sorted(revoked)}
    (folder / "index.json").write_text(json.dumps(index, indent=1))
    print(f"{step}: " + ", ".join(f"{ref['id']} ({ref['count']})" for ref in refs) + (f", removed {sorted(revoked)}" if revoked else ""))


def months(photos):
    return {"2026-09": photos[:FIRST_MONTH_SIZE], "2026-10": photos[FIRST_MONTH_SIZE:]}


def bad_photos(photos, count=50):
    """New photos whose files don't match their checksum: real files, new ids, wrong hashes, no videos."""
    bad = []
    for number, item in enumerate(photos[:count], start=1):
        copy = {key: value for key, value in item.items() if key != "video"}
        copy["id"] = f"test-bad-{number}"
        copy["sha256"] = "f" * 64
        bad.append(copy)
    return bad


def main():
    photos = real_photos()
    print(f"{len(photos)} live photos in the real feed")
    split = months(photos)
    command = sys.argv[1:] or ["all"]
    if command == ["all"]:
        write_step("month-1", {"2026-09": split["2026-09"]})
        write_step("month-2", split)
        write_step("bad-month", {**split, "2026-11": bad_photos(photos)})
    elif command[0] == "remove" and len(command) == 2:
        write_step("removal", split, revoked=[command[1]])
    elif command[0] == "broken" and len(command) == 2:
        write_step("broken-list", split, revoked=[command[1]], damaged={"2026-09"})
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
