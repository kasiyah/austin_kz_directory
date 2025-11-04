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
    business_name  = row['Business Name']
    slug = slugify(business_name)

    # Look for existing post file with this slug, any date
    pattern = os.path.join(posts_dir, f"*-{slug}.md")
    existing_files = glob.glob(pattern)

    if existing_files:
        print(f"Skipping existing business: {business_name}")
        skipped_count += 1
        continue

    # Create new post
    filename = f"{posts_dir}/{today}-{slug}.md"

    content = f"""---
title: "{row['Business Name']}"
category: "{row['Category']}"
date: {today}
tags: [{row['Tag']}]
---

{row['Notes']}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


    created_count += 1
    print(f"Created new post: {filename}")

print(f"\n✅ {created_count} new posts created, {skipped_count} skipped (already exist).")