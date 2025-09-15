#!/usr/bin/env python3
"""
scripts/rename_images.py

Rename images in doctors/images/ to SEO-friendly filenames and update _data/doctors.json
Image field updated to full path: /doctors/images/dr-<slug>.<ext>
"""
import os
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "_data" / "doctors.json"
IMAGE_DIR = ROOT / "doctors" / "images"

# Allowed image extensions
EXTS = [".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".avif", ".webp"]

def slugify(name: str) -> str:
    """
    - Remove honorifics like Dr., Doctor, Prof.
    - Cut off everything starting from MD, MS, MCh, or DM (case-insensitive).
    - Remove parentheticals like (Osmania).
    - Convert to lowercase, hyphenated.
    """
    if not name:
        return ""

    s = name.strip()

    # Remove common prefixes/honorifics
    s = re.sub(r"^(dr\.?|doctor|prof\.?|mr\.?|mrs\.?|ms\.?)\s+", "", s, flags=re.I)

    # Cut off at MD, MS, MCh, or DM (keep only the name before these tokens)
    s = re.split(r"\b(md|ms|mch|dm)\b", s, flags=re.I)[0]

    # Remove parentheticals like (Osmania)
    s = re.sub(r"\([^)]*\)", "", s)

    # Remove any trailing commas/extra whitespace
    s = s.strip(" ,")

    # Normalize: replace non-alphanum with hyphen, collapse multiple hyphens
    s = re.sub(r"[^a-z0-9]+", "-", s.lower())
    s = re.sub(r"-{2,}", "-", s)

    return s.strip("-")

def find_old_file_by_index(idx: int):
    """
    Try common filename patterns for an index:
    image1.webp, image 1.webp, image_1.webp, image-1.png, img001.jpg, IMG_0001.jpg etc.
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
        f"{idx}",  # literal digit anywhere
    ]
    if not IMAGE_DIR.exists():
        return None

    # First try explicit patterns with extensions
    for p in patterns:
        for ext in EXTS:
            candidate = IMAGE_DIR / (p + ext)
            if candidate.exists():
                return candidate

    # Next: try files that contain the index number anywhere in the name
    for f in IMAGE_DIR.iterdir():
        if not f.is_file():
            continue
        # look for the index as a standalone number or substring of numeric sequences in filename
        # e.g., image1, IMG_0001, photo-1
        if re.search(rf"\b{idx}\b", f.name) or str(idx) in re.findall(r"\d+", f.name):
            return f
    return None

# --- main ---
if not DATA_FILE.exists():
    print(f"ERROR: {_data/doctors.json} not found at {DATA_FILE}", file=sys.stderr)
    sys.exit(1)

# Load JSON
with DATA_FILE.open("r", encoding="utf-8") as fh:
    try:
        doctors = json.load(fh)
    except Exception as e:
        print("Failed to parse JSON:", e, file=sys.stderr)
        sys.exit(1)

changed = False
messages = []
updated_entries = []

for i, doc in enumerate(doctors, start=1):
    name = (doc.get("name") or "").strip()
    if not name:
        messages.append(f"[{i}] Missing name; skipping")
        continue

    # Build slug and basename
    slug = slugify(name)
    if not slug:
        slug = f"doctor-{i}"
    # ensure single 'dr-' prefix
    new_basename = slug if slug.startswith("dr-") else f"dr-{slug}"

    # Determine old path:
    old_path = None
    avatar_field = str(doc.get("image", "") or "").strip()
    if avatar_field:
        candidate = avatar_field.lstrip("/").split("/")[-1]
        cand_path = IMAGE_DIR / candidate
        if cand_path.exists():
            old_path = cand_path
        else:
            base_no_ext = Path(candidate).stem
            for ext in EXTS:
                p = IMAGE_DIR / (base_no_ext + ext)
                if p.exists():
                    old_path = p
                    break

    if old_path is None:
        old_path = find_old_file_by_index(i)

    if old_path and old_path.exists():
        ext = old_path.suffix.lower() if old_path.suffix else ".webp"
        new_name = f"{new_basename}{ext}"
        new_path = IMAGE_DIR / new_name

        # If already correct (same file), just set JSON path properly
        try:
            if old_path.resolve() == new_path.resolve():
                messages.append(f"[{i}] Already named: {new_name}")
                # ensure image field uses full path
                desired_image_field = f"/doctors/images/{new_name}"
                if doc.get("image") != desired_image_field:
                    doc["image"] = desired_image_field
                    changed = True
                    updated_entries.append((name, new_name))
            else:
                # If target exists and is different file, create unique filename to avoid clobbering
                if new_path.exists() and new_path.resolve() != old_path.resolve():
                    k = 1
                    base = new_basename
                    while True:
                        candidate = IMAGE_DIR / f"{base}-{k}{ext}"
                        if not candidate.exists():
                            new_path = candidate
                            new_name = candidate.name
                            break
                        k += 1
                print(f"Renaming: {old_path.name} -> {new_name}")
                old_path.rename(new_path)
                doc["image"] = f"/doctors/images/{new_name}"
                changed = True
                updated_entries.append((name, new_name))
        except Exception as e:
            messages.append(f"[{i}] Error renaming {old_path.name}: {e}")
    else:
        # No existing file found: set JSON to the expected path (no file is created)
        default_name = f"{new_basename}.webp"
        desired_image_field = f"/doctors/images/{default_name}"
        if doc.get("image") != desired_image_field:
            messages.append(f"[{i}] No file found for '{name}'. Setting image field to '{desired_image_field}' (file missing).")
            doc["image"] = desired_image_field
            changed = True
            updated_entries.append((name, default_name))
        else:
            messages.append(f"[{i}] No file found for '{name}', image already set to {desired_image_field}")

# Write back JSON only if changes were made
if changed:
    # make a backup of the original JSON
    backup = DATA_FILE.with_suffix(".json.bak")
    try:
        DATA_FILE.replace(backup)  # atomic-ish rename
    except Exception:
        # fallback: copy
        import shutil
        shutil.copy2(DATA_FILE, backup)
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(doctors, fh, indent=2, ensure_ascii=False)
    print("Updated JSON and saved backup:", backup.name)
else:
    print("No changes to JSON required.")

# Print summary
if updated_entries:
    print("Updated entries (name -> image):")
    for name, new_name in updated_entries:
        print(f"  {name} -> {new_name}")
else:
    print("No image renames/JSON updates performed.")

for m in messages:
    print(m)

print("Done.")
sys.exit(0)
