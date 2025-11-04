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

# Ensure _posts directory exists
posts_dir = "_posts"
os.makedirs(posts_dir, exist_ok=True)

# Set timezone (US Central)
central = ZoneInfo("America/Chicago")
today = datetime.now(tz=central).strftime("%Y-%m-%d")

def safe_str(value):
    """Convert value to string, return empty string if NaN or None"""
    if pd.isna(value):
        return ""
    return str(value).strip()

def make_clickable_link(value, prefix=""):
    """Return Markdown clickable link if value is not empty"""
    value = safe_str(value)
    if not value:
        return ""
    if prefix == "https://" and not value.startswith(("http://", "https://")):
        value = prefix + value
    if prefix == "mailto:":
        return f"[{value}]({prefix}{value})"
    return f"[{value}]({value})"

# Counters
created_count = 0
skipped_count = 0

for _, row in df.iterrows():
    # Title source: Business Name or fallback to Owner Name
    title_source = safe_str(row.get("Business Name")) or safe_str(row.get("Owner Name"))
    slug = slugify(title_source)

    # Skip if post exists
    pattern = os.path.join(posts_dir, f"*-{slug}.md")
    if glob.glob(pattern):
        print(f"Skipping existing business: {title_source}")
        skipped_count += 1
        continue

    # Process tags (dropdown may contain multiple)
    raw_tags = safe_str(row.get("Tag")).replace("\n", ",").replace(";", ",")
    tags_list = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]

    # Include region
    region = safe_str(row.get("Region"))
    if region:
        tags_list.append(region)

    tags_yaml = ", ".join(tags_list)

    # Links section (only if exists)
    website_link = make_clickable_link(row.get("Website"), prefix="https://")
    email_link = make_clickable_link(row.get("Email"), prefix="mailto:")
    instagram_link = make_clickable_link(row.get("Instagram"), prefix="https://")
    facebook_link = make_clickable_link(row.get("Facebook"), prefix="https://")
    phone_value = safe_str(row.get("Phone"))
    address_value = safe_str(row.get("Address"))

    links = []
    if website_link:
        links.append(f"Website: {website_link}")
    if email_link:
        links.append(f"Email: {email_link}")
    if instagram_link:
        links.append(f"Instagram: {instagram_link}")
    if facebook_link:
        links.append(f"Facebook: {facebook_link}")
    if phone_value:
        links.append(f"Phone: {phone_value}")
    if address_value:
        links.append(f"Address: {address_value}")

    links_section = "\n\n".join(links) if links else ""

    # Owner line before notes
    owner_name = safe_str(row.get("Owner Name"))
    owner_line = f" {owner_name}\n\n" if owner_name else ""

    # Build Markdown content
    content = f"""---
title: "{title_source}"
category: "{safe_str(row.get('Category'))}"
date: {today}
tags: [{tags_yaml}]
---

{owner_line}{safe_str(row.get('Notes'))}

{links_section}
"""

    # Write file
    filename = os.path.join(posts_dir, f"{today}-{slug}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    created_count += 1
    print(f"Created new post: {filename}")

print(f"\n!!! {created_count} new posts created, {skipped_count} skipped (already exist).")
