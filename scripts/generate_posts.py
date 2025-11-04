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

def safe_str(value):
    """Convert value to string, return empty string if NaN or None"""
    if pd.isna(value):
        return ""
    return str(value).strip()

# Generate Markdown posts
created_count = 0
skipped_count = 0

for _, row in df.iterrows():
    # Use Business Name or Owner Name if missing
    title_source = safe_str(row.get("Business Name"))
    if not title_source:
        title_source = safe_str(row.get("Owner Name"))
    
    slug = slugify(title_source)

    # Skip if post already exists
    pattern = os.path.join(posts_dir, f"*-{slug}.md")
    if glob.glob(pattern):
        print(f"Skipping existing business: {title_source}")
        skipped_count += 1
        continue

    # Process multiple tags
    raw_tags = safe_str(row.get("Tag"))
    tags_list = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    tags_yaml = ", ".join(tags_list)

    # Build content
    content = f"""---
title: "{title_source}"
category: "{safe_str(row.get('Category'))}"
owner: "{safe_str(row.get('Owner Name'))}"
website: "{safe_str(row.get('Website'))}"
email: "{safe_str(row.get('Email'))}"
instagram: "{safe_str(row.get('Instagram'))}"
facebook: "{safe_str(row.get('Facebook'))}"
phone: "{safe_str(row.get('Phone'))}"
date: {today}
region: "{safe_str(row.get('Region'))}"
tags: [{tags_yaml}]
---

{safe_str(row.get('Notes'))}
"""

    filename = os.path.join(posts_dir, f"{today}-{slug}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    created_count += 1
    print(f"Created new post: {filename}")

print(f"\n!!! {created_count} new posts created, {skipped_count} skipped (already exist).")