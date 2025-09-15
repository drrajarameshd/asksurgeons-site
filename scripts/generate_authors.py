#!/usr/bin/env python3
"""
scripts/generate_authors.py
Generates _authors/<slug>.md files from _data/doctors.json
Designed for GitHub Actions.
"""
import json
import re
from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "_data" / "doctors.json"
AUTHORS_DIR = ROOT / "_authors"
IMAGE_DIR = ROOT / "doctors" / "images"

# Helper: make a clean slug (strip honorifics, cut off at MD/MS/MCh/DM)
def slugify(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    # remove parenthetical notes e.g. (Osmania)
    s = re.sub(r"\([^)]*\)", "", s)
    # remove honorifics at start
    s = re.sub(r"^(dr\.?|doctor|prof\.?|mr\.?|mrs\.?|ms\.?)\s+", "", s, flags=re.I)
    # cut off at MD, MS, MCh, DM (keep only part before these tokens)
    s = re.split(r"\b(md|ms|mch|dm)\b", s, flags=re.I)[0]
    # remove trailing commas/extra whitespace
    s = s.strip(" ,")
    # replace non-alphanumeric with hyphen and collapse multiple hyphens
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
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
    if s is None:
        return ""
    s = str(s)
    s = s.replace('"""', '\\"\\\"\\"')
    return s

written = []

for doc in doctors:
    # Map fields
    name = doc.get("name") or doc.get("full_name") or "Unknown"
    speciality = doc.get("speciality") or doc.get("role") or doc.get("department") or ""
    avatar_field = (doc.get("image") or doc.get("avatar") or "").strip()
    bio = doc.get("bio") or doc.get("description") or ""
    department = doc.get("department") or speciality or ""

    # build slug from name (for filename & permalink)
    slug = slugify(name)
    if not slug:
        slug = f"doctor-{int(datetime.utcnow().timestamp())}"

    # Build author filename
    filename = AUTHORS_DIR / f"{slug}.md"

    # Normalize avatar to absolute site path if possible.
    avatar = ""
    if avatar_field:
        # if already an absolute path (/doctors/images/...), keep as-is
        if avatar_field.startswith("/"):
            avatar = avatar_field
        else:
            # if it's just a filename (dr-foo.webp) or relative path, use /doctors/images/<basename>
            basename = Path(avatar_field).name
            avatar = f"/doctors/images/{basename}"
    else:
        # If no avatar provided, attempt to predict filename from slug
        # (we don't create files, just set the expected path)
        avatar = f"/doctors/images/dr-{slug}.webp"

    # If image file actually exists in repo, ensure avatar points to that existing filename
    try:
        # if avatar is like /doctors/images/<name>, check for file existence
        if avatar.startswith("/doctors/images/"):
            candidate = IMAGE_DIR / Path(avatar).name
            if candidate.exists():
                avatar = f"/doctors/images/{candidate.name}"
            else:
                # if not found, leave avatar as the expected path (so templates can use it later)
                pass
    except Exception:
        pass

    # Build front matter (use YAML block scalar for bio)
    fm_lines = [
        "---",
        f'name: "{name}"',
        f'title: "{name}"',
        f'role: "{speciality}"',
    ]
    if avatar:
        fm_lines.append(f'avatar: "{avatar}"')

    if bio:
        fm_lines.append("bio: |")
        for line in str(bio).splitlines():
            fm_lines.append(f"  {line}")
    if department:
        fm_lines.append(f'department: "{department}"')

    fm_lines.append(f'permalink: "/doctors/{slug}/"')
    fm_lines.append("---")
    fm_lines.append("")  # final newline

    content = "\n".join(fm_lines)

    # Only write if changed
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
