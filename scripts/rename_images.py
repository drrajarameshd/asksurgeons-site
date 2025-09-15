#!/usr/bin/env python3
"""
scripts/rename_images.py
Rename images in doctors/images/ to SEO-friendly filenames and update _data/doctors.json.

Usage:
  python scripts/rename_images.py
"""
import os
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "_data" / "doctors.json"
IMAGE_DIR = ROOT / "doctors" / "images"

# Allowed image extensions (order matters when detecting)
EXTS = [".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg"]

def slugify(name: str) -> str:
    s = name.lower().strip()
    # remove titles in parentheses e.g. (Osmania)
    s = re.sub(r"\([^)]*\)", "", s)
    # replace non-alphanum with hyphen
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")

def find_old_file_by_index(idx: int):
    """
    attempt various common patterns for existing files:
    image1.webp, image 1.webp, image_1.webp, image-1.webp, IMG_0001.webp etc.
    Returns Path or None
    """
    patterns = [
        f"image{idx}",
        f"image-{idx}",
        f"image_{idx}",
        f"image {idx}",
        f"img{idx}",
        f"img-{idx}",
        f"img_{idx}",
        f"IMG_{idx}",
    ]
    for p in patterns:
        for ext in EXTS:
            candidate = IMAGE_DIR / (p + ext)
            if candidate.exists():
                return candidate
    # also try any file that contains the index digits e.g. image1 (with spaces)
    for f in IMAGE_DIR.iterdir() if IMAGE_DIR.exists() else []:
        name = f.name.lower()
        if str(idx) in re.findall(r"\d+", name):
            return f
    return None

if not DATA_FILE.exists():
    print(f"ERROR: {DATA_FILE} not found", file=sys.stderr)
    sys.exit(1)

if not IMAGE_DIR.exists():
    print(f"WARNING: Image directory {IMAGE_DIR} does not exist. Will still update JSON if needed.")

with DATA_FILE.open("r", encoding="utf-8") as fh:
    doctors = json.load(fh)

changed = False
messages = []

for i, doc in enumerate(doctors, start=1):
    name = doc.get("name", "").strip()
    if not name:
        messages.append(f"[{i}] Missing name; skipping")
        continue
    slug = slugify(name)
    if not slug:
        slug = f"doctor-{i}"

    # choose extension from existing image or default to .webp
    new_basename = f"dr-{slug}"
    # try to detect old image: either provided in JSON or fallback to pattern search
    avatar_field = doc.get("image", "") or ""
    old_path = None
    if avatar_field:
        # avatar might be "doctors/images/image1.webp" or "image1.webp" or "/doctors/images/image1.webp"
        candidate = avatar_field.lstrip("/").split("/")[-1]
        cand_path = IMAGE_DIR / candidate
        if cand_path.exists():
            old_path = cand_path
        else:
            # try patterns with same basename but different ext
            base_no_ext = Path(candidate).stem
            for ext in EXTS:
                p = IMAGE_DIR / (base_no_ext + ext)
                if p.exists():
                    old_path = p
                    break

    if old_path is None:
        # fallback: try to find file by numeric index i
        old_path = find_old_file_by_index(i)

    if old_path and old_path.exists():
        ext = old_path.suffix.lower() or ".webp"
        new_name = f"{new_basename}{ext}"
        new_path = IMAGE_DIR / new_name
        # avoid renaming if name already matches
        if old_path.resolve() == new_path.resolve():
            messages.append(f"[{i}] Skipped rename (already): {old_path.name}")
        else:
            # if target exists, add a numeric suffix to avoid clobbering
            if new_path.exists():
                # if existing file is the same as old_path, okay; else create unique name
                if new_path.resolve() != old_path.resolve():
                    k = 1
                    while True:
                        candidate = IMAGE_DIR / f"{new_basename}-{k}{ext}"
                        if not candidate.exists():
                            new_path = candidate
                            new_name = candidate.name
                            break
                        k += 1
            print(f"Renaming: {old_path.name} -> {new_name}")
            old_path.rename(new_path)
            doc["image"] = new_name
            changed = True
    else:
        # no file found for this doctor — still update JSON to a normalized default filename if image field existed
        # but do not create files
        default_name = f"{new_basename}.webp"
        current_image = doc.get("image", "")
        if current_image != default_name:
            messages.append(f"[{i}] No file found for '{name}'. Setting image field to '{default_name}' (file missing).")
            doc["image"] = default_name
            changed = True
        else:
            messages.append(f"[{i}] No file found for '{name}', image already set to {default_name}")

# Write back JSON only if changes were made
if changed:
    # keep a backup
    backup = DATA_FILE.with_suffix(".json.bak")
    DATA_FILE.rename(backup)
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(doctors, fh, indent=2, ensure_ascii=False)
    print("Updated JSON and backed up original to:", backup.name)
else:
    print("No changes to JSON required.")

for m in messages:
    print(m)

print("Done.")
# exit 0
sys.exit(0)
