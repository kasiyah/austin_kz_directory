import pandas as pd
import os
from datetime import datetime
from slugify import slugify  # pip install python-slugify

# 1️⃣ CSV URL from published Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSgj8rixng0uRdpfNuMpvLVbug5FbLqw1MiHlO2Tb4z06eaB7c3UE6DKpzS6svvZLDdKKgsx5CULcJM/pub?gid=0&single=true&output=csv"

# 2️⃣ Read CSV
df = pd.read_csv(csv_url)

# 3️⃣ Make sure _posts directory exists
posts_dir = "_posts"
os.makedirs(posts_dir, exist_ok=True)

# 4️⃣ Generate Markdown posts
for index, row in df.iterrows():
    slug = slugify(row['Business Name'])
    date = datetime.today().strftime("%Y-%m-%d")
    filename = f"{posts_dir}/{date}-{slug}.md"

    content = f"""---
title: "{row['Business Name']}"
category: "{row['Category']}"
date: {date}
tags: [{row['Tag']}]
---

{row['Notes']}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

print(f"{len(df)} posts generated in {posts_dir}/")