# Community Business Directory

A directory of local businesses, services, and places for our Kazakh community in the Austin, Texas area. It started as a shared document in a group chat and is now a searchable website with a page for every listing.

**Live site:** https://kasiyah.github.io/austin_kz_directory/ 

## Why this exists

A long shared document is hard to search, hard to keep tidy, and awkward on a phone. This project keeps all listings in one spreadsheet that anyone can maintain, and turns it into a fast static website with categories, tags, and a page per business.

## How it works

1. **Spreadsheet:** each row is one business (name, category, tags, region, contact links, notes).
2. **Publish button:** a Google Apps Script adds a **Site → Publish to site** menu to the sheet. It tells GitHub that the data has changed.
3. **Generate:** a GitHub Actions workflow runs a Python script that reads the sheet as CSV and writes one Markdown post per business into `_posts/`, then commits the changes.
4. **Build and deploy:** Jekyll builds the site with the Chirpy theme and publishes it to GitHub Pages.

Editing the spreadsheet and clicking publish is all it takes to update the live site.

## Tech stack

- **Site:** Jekyll with the Chirpy theme, hosted on GitHub Pages
- **Automation:** GitHub Actions
- **Data processing:** Python (pandas, python-slugify)
- **Data source and trigger:** Google Sheets and Google Apps Script

## Repository layout

| Path | Purpose |
|---|---|
| `scripts/generate_posts.py` | Reads the sheet and writes the business posts |
| `_posts/` | Generated business pages (do not edit by hand) |
| `.github/workflows/` | Deploy workflow and pull request checks |
| `.github/CONTRIBUTING.md` | Branching policy and how changes are made |

## Engineering notes

- **Event-driven deploys:** the sheet triggers the workflow through GitHub's `repository_dispatch` event, so builds run only when the data changes instead of on a fixed schedule.
- **Safe pipeline:** runs are queued with concurrency control so deployments never overlap, and the deploy jobs run only on `main`.
- **Reviewed changes:** code changes go through pull requests with an automated build check before they reach `main`.

## Run it locally

```bash
# Build and preview the site
bundle install
bundle exec jekyll serve

# Regenerate posts from the sheet (needs the published sheet URL set in the script)
pip install pandas python-slugify
python scripts/generate_posts.py
```

Running the generator writes files into `_posts/`. Do not commit generated posts from a feature branch, because the workflow commits them on `main`. See `.github/CONTRIBUTING.md` for details.




# Chirpy Starter

[![Gem Version](https://img.shields.io/gem/v/jekyll-theme-chirpy)][gem]&nbsp;
[![GitHub license](https://img.shields.io/github/license/cotes2020/chirpy-starter.svg?color=blue)][mit]

When installing the [**Chirpy**][chirpy] theme through [RubyGems.org][gem], Jekyll can only read files in the folders
`_data`, `_layouts`, `_includes`, `_sass` and `assets`, as well as a small part of options of the `_config.yml` file
from the theme's gem. If you have ever installed this theme gem, you can use the command
`bundle info --path jekyll-theme-chirpy` to locate these files.

The Jekyll team claims that this is to leave the ball in the user’s court, but this also results in users not being
able to enjoy the out-of-the-box experience when using feature-rich themes.

To fully use all the features of **Chirpy**, you need to copy the other critical files from the theme's gem to your
Jekyll site. The following is a list of targets:

```shell
.
├── _config.yml
├── _plugins
├── _tabs
└── index.html
```

To save you time, and also in case you lose some files while copying, we extract those files/configurations of the
latest version of the **Chirpy** theme and the [CD][CD] workflow to here, so that you can start writing in minutes.

## Prerequisites

Follow the instructions in the [Jekyll Docs](https://jekyllrb.com/docs/installation/) to complete the installation of
the basic environment. [Git](https://git-scm.com/) also needs to be installed.

## Installation

Sign in to GitHub and [**use this template**][use-template] to generate a brand new repository and name it
`USERNAME.github.io`, where `USERNAME` represents your GitHub username.

Then clone it to your local machine and run:

```console
$ bundle
```

## Usage

Please see the [theme's docs](https://github.com/cotes2020/jekyll-theme-chirpy#documentation).

## License

This work is published under [MIT][mit] License.

[gem]: https://rubygems.org/gems/jekyll-theme-chirpy
[chirpy]: https://github.com/cotes2020/jekyll-theme-chirpy/
[use-template]: https://github.com/cotes2020/chirpy-starter/generate
[CD]: https://en.wikipedia.org/wiki/Continuous_deployment
[mit]: https://github.com/cotes2020/chirpy-starter/blob/master/LICENSE
