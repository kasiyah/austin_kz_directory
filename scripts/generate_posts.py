import pandas as pd
import os
import re
import sys
from datetime import datetime
from slugify import slugify  # pip install python-slugify
from zoneinfo import ZoneInfo  # Python 3.9+

# CSV URL from published Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTC5rCFcQcMSzcZdv9I1UkQdSjG2f1yA7gyrueAUjiR74amhx80ug92lksOA7NyeMTKwE7pBTvWaXFc/pub?gid=0&single=true&output=csv"

# Read the CSV. dtype=str keeps phone numbers and similar values as text
# (otherwise pandas can turn 5125551234 into 5125551234.0 when a column has blanks).
df = pd.read_csv(csv_url, dtype=str)

# Safety check: stop if the CSV looks wrong (empty, or Google returned
# something unexpected). Exiting with an error means nothing gets committed.
if df.empty or "Business Name" not in df.columns:
    print("ERROR: CSV is empty or has no 'Business Name' column. Nothing was changed.")
    sys.exit(1)

# Ensure _posts directory exists
posts_dir = "_posts"
os.makedirs(posts_dir, exist_ok=True)

# Set timezone (US Central)
central = ZoneInfo("America/Chicago")
today = datetime.now(tz=central).strftime("%Y-%m-%d")

# Every post written by this script carries this line in its front matter.
# Only posts with the marker are ever deleted, so hand-written posts
# (or the theme's sample posts) are never touched.
MARKER_LINE = "auto_generated: true"
MARKER_RE = re.compile(r"(?m)^auto_generated:\s*true\s*$")
POST_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def safe_str(value):
    """Convert value to string, return empty string if NaN or None"""
    if pd.isna(value):
        return ""
    return str(value).strip()


def yaml_escape(value):
    """Escape a value so it is safe inside double quotes in YAML front matter"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


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


def is_auto_generated(path):
    """True if the post's front matter contains the auto_generated marker"""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    return len(parts) >= 3 and bool(MARKER_RE.search(parts[1]))


# Index the existing posts by slug (the part of the file name after the date)
existing_posts = {}          # slug -> file path
auto_generated_slugs = set() # slugs of posts this script created
for name in sorted(os.listdir(posts_dir)):
    match = POST_RE.match(name)
    if not match:
        continue
    path = os.path.join(posts_dir, name)
    slug = match.group(2)
    existing_posts.setdefault(slug, path)
    if is_auto_generated(path):
        auto_generated_slugs.add(slug)

# Counters
created_count = 0
updated_count = 0
unchanged_count = 0
deleted_count = 0
duplicate_count = 0

current_slugs = set()  # slugs of every business currently in the sheet

for _, row in df.iterrows():
    # Title source: Business Name or fallback to Owner Name
    title_source = safe_str(row.get("Business Name")) or safe_str(row.get("Owner Name"))
    slug = slugify(title_source)

    # Skip empty or junk rows
    if not slug:
        continue

    # Two rows with the same name would fight over one file, so keep the first
    if slug in current_slugs:
        print(f"Skipping duplicate name in sheet: {title_source}")
        duplicate_count += 1
        continue
    current_slugs.add(slug)

    # If a post already exists, keep its file name (and original date)
    existing = existing_posts.get(slug)
    if existing:
        filename = existing
        post_date = os.path.basename(existing)[:10]
    else:
        post_date = today
        filename = os.path.join(posts_dir, f"{today}-{slug}.md")

    # Process tags (dropdown may contain multiple)
    raw_tags = safe_str(row.get("Tags")).replace("\n", ",").replace(";", ",")
    tags_list = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]

    # Include region
    region = safe_str(row.get("Region"))
    if region:
        tags_list.append(region)

    # Quote each tag so characters like ':' or '&' cannot break the YAML
    tags_yaml = ", ".join(f'"{yaml_escape(tag)}"' for tag in tags_list)

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
title: "{yaml_escape(title_source)}"
category: "{yaml_escape(safe_str(row.get('Category')))}"
date: {post_date}
tags: [{tags_yaml}]
{MARKER_LINE}
---

{owner_line}{safe_str(row.get('Notes'))}\n\n\n{safe_str(row.get('Source Text'))}

{links_section}
"""

    if existing:
        # Only rewrite the file if the sheet data actually changed
        with open(filename, "r", encoding="utf-8") as f:
            if f.read() == content:
                unchanged_count += 1
                continue
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        updated_count += 1
        print(f"Updated post: {filename}")
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        created_count += 1
        print(f"Created new post: {filename}")

# Delete posts that this script created but whose business is no longer in the
# sheet. This is what removes the old post when a business is renamed: the new
# name gets a new post above, and the old name's post is removed here.
orphans = [
    (slug, path)
    for slug, path in existing_posts.items()
    if slug in auto_generated_slugs and slug not in current_slugs
]

# Safety guard: if the sheet suddenly looks like it lost most of its rows
# (bad download, accidentally cleared sheet), stop instead of deleting.
if len(orphans) > 3 and len(orphans) > len(auto_generated_slugs) / 2:
    print(
        f"ERROR: this run would delete {len(orphans)} of {len(auto_generated_slugs)} "
        "generated posts. That looks like a bad CSV, so nothing was committed. "
        "If it is intentional, delete the posts by hand."
    )
    sys.exit(1)

for slug, path in orphans:
    os.remove(path)
    deleted_count += 1
    print(f"Deleted post no longer in the sheet: {path}")

print(
    f"\n!!! {created_count} created, {updated_count} updated, "
    f"{unchanged_count} unchanged, {deleted_count} deleted, "
    f"{duplicate_count} duplicate names skipped."
)