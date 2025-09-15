#!/usr/bin/env python3
"""
scripts/generate_authors.py
Generates _authors/<slug>.md files from _data/doctors.json
Designed for GitHub Actions.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
import sys
import html

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "_data" / "doctors.json"
AUTHORS_DIR = ROOT / "_authors"

# Helper: make a clean slug
def slugify(s: str) -> str:
    s = s.lower().strip()
    # replace spaces, slashes, commas with hyphen
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")

# Read data
if not DATA_FILE.exists():
    print(f"ERROR: {_data/doctors.json} not found at {DATA_FILE}", file=sys.stderr)
    sys.exit(1)

with DATA_FILE.open("r", encoding="utf-8") as f:
    try:
        doctors = json.load(f)
    except Exception as e:
        print("Failed to parse JSON:", e, file=sys.stderr)
        sys.exit(1)

AUTHORS_DIR.mkdir(parents=True, exist_ok=True)

def safe_yaml_string(s: str) -> str:
    # escape quotes and preserve newlines
    if s is None:
        return ""
    s = str(s)
    s = s.replace('"""', '\\"\\\"\\"')  # avoid triple quote conflicts
    # prefer using "|" block scalar for longer bios
    return s

written = []

for doc in doctors:
    # Map common fields (adjust keys if your JSON differs)
    name = doc.get("name") or doc.get("full_name") or "Unknown"
    speciality = doc.get("speciality") or doc.get("role") or doc.get("department") or ""
    avatar = doc.get("image") or doc.get("avatar") or ""
    # ensure avatar path is absolute-style (starts with /) for site links
    if avatar and not avatar.startswith("/"):
        avatar = avatar.lstrip("/")
        avatar = f"/{avatar}"
    bio = doc.get("bio") or doc.get("description") or ""
    department = doc.get("department") or speciality or ""
    # build slug from name
    slug = slugify(name)
    if not slug:
        slug = f"doctor-{int(datetime.utcnow().timestamp())}"

    filename = AUTHORS_DIR / f"{slug}.md"

    # Build front matter (use YAML block scalar for bio if long)
    fm_lines = [
        "---",
        f'name: "{name}"',
        f'title: "{name}"',
        f'role: "{speciality}"',
    ]
    if avatar:
        fm_lines.append(f'avatar: "{avatar}"')
    # Use a block scalar for bio to preserve newlines and special characters
    if bio:
        # indent the block content properly
        fm_lines.append("bio: |")
        for line in bio.splitlines():
            fm_lines.append(f"  {line}")
    if department:
        fm_lines.append(f'department: "{department}"')
    fm_lines.append(f'permalink: "/doctors/{slug}/"')
    fm_lines.append("---")
    fm_lines.append("")  # final newline

    content = "\n".join(fm_lines)
    # Only write if changed (minimizes git noise)
    write_file = True
    if filename.exists():
        old = filename.read_text(encoding="utf-8")
        if old == content:
            write_file = False

    if write_file:
        filename.write_text(content, encoding="utf-8")
        print("Wrote:", filename.relative_to(ROOT))
        written.append(str(filename.relative_to(ROOT)))
    else:
        print("Unchanged:", filename.relative_to(ROOT))

if not written:
    print("No files written. Everything up-to-date.")
else:
    print("Generated files:", written)
