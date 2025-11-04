import pandas as pd
import os
from datetime import datetime
from slugify import slugify  # pip install python-slugify
from zoneinfo import ZoneInfo  # Python 3.9+
import glob

# CSV URL from published Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSgj8rixng0uRdpfNuMpvLVbug5FbLqw1MiHlO2Tb4z06eaB7c3UE6DKpzS6svvZLDdKKgsx5CULcJM/pub?gid=0&single=true&output=csv"

# Read CSV
df = pd.read_csv(csv_url)

# Make sure _posts directory exists
posts_dir = "_posts"
os.makedirs(posts_dir, exist_ok=True)

# Set desired timezone (US Central)
central = ZoneInfo("America/Chicago")
today = datetime.now(tz=central).strftime("%Y-%m-%d")

# Generate Markdown posts
created_count = 0
skipped_count = 0

for index, row in df.iterrows():
    title_source = str(row.get("Business Name")).strip()
    if not title_source or title_source.lower() in ["nan", ""]:
        title_source = str(row.get("Owner Name")).strip()
    slug = slugify(title_source)

    # Look for existing post file with this slug, any date
    pattern = os.path.join(posts_dir, f"*-{slug}.md")
    existing_files = glob.glob(pattern)

    if existing_files:
        print(f"Skipping existing business: {title_source}")
        skipped_count += 1
        continue

    # Create new post
    filename = f"{posts_dir}/{today}-{slug}.md"

     # Process multiple tags
    raw_tags = str(row.get("Tag", "")).strip()
    if raw_tags:
        # Split on commas and strip spaces
        tags_list = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
        tags_yaml = ", ".join(tags_list)
    else:
        tags_yaml = ""

    content = f"""---
title: "{title_source}"
category: "{row.get('Category', '').strip()}"
owner: "{row.get('Owner Name', '').strip()}"
website: "{row.get('Website', '').strip()}"
email: "{row.get('Email', '').strip()}"
instagram: "{row.get('Instagram', '').strip()}"
facebook: "{row.get('Facebook', '').strip()}"
phone: "{row.get('Phone', '').strip()}"
date: {today}
region: "{row.get('Region', '').strip()}"
tags: [{tags_yaml}]
---

{row['Notes']}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


    created_count += 1
    print(f"Created new post: {filename}")

print(f"\n!!! {created_count} new posts created, {skipped_count} skipped (already exist).")