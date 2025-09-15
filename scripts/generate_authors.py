#!/usr/bin/env python3
# scripts/generate_authors.py

import json, re, os, sys

def slug(s):
    return re.sub(r'[^a-z0-9\\-]+','-', s.lower()).strip('-')

# find doctors.json in likely locations
possible_paths = [
    "_data/doctors.json",
    "doctors.json",
    os.path.join(os.getcwd(), "_data", "doctors.json")
]
data_path = None
for p in possible_paths:
    if os.path.exists(p):
        data_path = p
        break

if not data_path:
    print("Error: doctors.json not found. Looked at:", ", ".join(possible_paths))
    sys.exit(2)

with open(data_path, "r", encoding="utf8") as fh:
    data = json.load(fh)

os.makedirs("_authors", exist_ok=True)
generated = []

for d in data:
    name = d.get("name", "").split(",")[0].strip()
    if not name:
        name = "unnamed"
    fn = slug(name) or slug(d.get("name", "unnamed"))
    image = d.get("image", "")
    bio = d.get("bio", "").replace('"','\\"')
    md = f"""---
name: "{d.get('name','')}"
layout: single
title: "{name}"
role: "{d.get('speciality','')}"
avatar: /{image.lstrip('/')}
bio: "{bio}"
department: "{d.get('department','')}"
permalink: /doctors/{fn}/
---
"""
    out_path = os.path.join("_authors", f"{fn}.md")
    with open(out_path, "w", encoding="utf8") as out:
        out.write(md)
    generated.append(out_path)

print(f"Generated {len(generated)} files.")
for p in generated[:20]:
    print(" -", p)
