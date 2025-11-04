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

def make_clickable_link(value, prefix=""):
    """Return Markdown clickable link if value is not empty"""
    value = safe_str(value)
    if not value:
        return ""
    if prefix == "https://" and not value.startswith(("http://", "https://")):
        value = prefix + value
    if prefix == "mailto:":
        return f"[{value}]({prefix}{value})"
    else:
        return f"[{value}]({value})"

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
    
    # Include region if present
    region = safe_str(row.get("Region"))
    if region:
        tags_list.append(region)

    tags_yaml = ", ".join(tags_list)

    # Prepare clickable links
    website_link = make_clickable_link(row.get("Website"), prefix="https://")
    email_link = make_clickable_link(row.get("Email"), prefix="mailto:")
    instagram_link = make_clickable_link(row.get("Instagram"), prefix="https://")
    facebook_link = make_clickable_link(row.get("Facebook"), prefix="https://")
    phone_value = safe_str(row.get("Phone"))
    address_value = safe_str(row.get("Address"))  # Optional

    links_section = ""
    if any([website_link, email_link, instagram_link, facebook_link, phone_value, address_value]):
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
        # Join with two newlines for separate paragraphs
        links_section = "\n\n".join(links)

    # Include owner line only if it exists
    owner_line = ""
    owner_name = safe_str(row.get("Owner Name"))
    if owner_name:
        owner_line = f"**Owner:** {owner_name}\n\n"

    # Build content
    content = f"""---
title: "{title_source}"
category: "{safe_str(row.get('Category'))}"
date: {today}
tags: [{tags_yaml}]
---

{owner_line}{safe_str(row.get('Notes'))}

{links_section}
"""

    filename = os.path.join(posts_dir, f"{today}-{slug}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    created_count += 1
    print(f"Created new post: {filename}")

print(f"\n!!! {created_count} new posts created, {skipped_count} skipped (already exist).")
