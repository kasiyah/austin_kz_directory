# Contributing: branching policy

This repository is a Jekyll directory site published on GitHub Pages. Business posts are generated from a Google Sheet by `scripts/generate_posts.py` and deployed by GitHub Actions. This page explains how we use branches so the live site stays safe.

## The short version

- `main` is the only permanent branch. Merging into it publishes the site.
- Every change is made on a short-lived branch, merged through a pull request, and the branch is deleted afterwards.
- One issue = one branch = one pull request.

## Branches

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Production. Anything merged here is deployed. The workflow bot also commits generated posts here. | Permanent |
| `<type>/<issue>-<description>` | One task, named as described below. | Deleted after merge |
| `dependabot/...` | Created automatically by Dependabot (once enabled). Leave the names as they are. | Deleted after merge |

We do not use `develop`, `staging`, or other long-lived branches. A pull request plus the build check is our safety step.

## Naming

Format: `<type>/<issue-number>-<short-description>`

| Type | Use for | Example |
|---|---|---|
| `feat/` | New or changed site features and script behavior | `feat/14-tel-and-map-links` |
| `fix/` | Bug fixes | `fix/22-escape-quotes-in-titles` |
| `ci/` | Workflows, Dependabot, build checks | `ci/20-pr-build-check` |
| `docs/` | README, editing guides | `docs/23-sheet-editing-guide` |
| `chore/` | Cleanup and manual dependency updates | `chore/24-update-gems` |
| `exp/` | Throwaway experiments with no issue yet | `exp/map-view` |

Rules:

1. Use lowercase letters, numbers, and hyphens only, with 2 to 5 words in the description.
2. Use the real issue number. Experiments without an issue use `exp/<description>`.
3. Do not use vague names such as `test`, `new-branch`, or `final-v2`.

## Workflow for a change

1. Pick an issue (or create one) and move its card to **In Progress**.
2. Branch from an up-to-date `main`:

   ```bash
   git switch main
   git pull
   git switch -c feat/14-tel-and-map-links
   ```

3. Commit in small steps with short messages in the imperative, for example `Add tel: links for phone numbers`.
4. Push the branch and open a pull request into `main`. Write `Closes #14` in the description so merging closes the issue and moves its card to **Done**.
5. Wait for the PR build check (once it exists) and fix any failures.
6. Merge with **Squash and merge**. The branch is deleted automatically.
7. Check that the workflow run on `main` succeeded.
8. Tidy up locally:

   ```bash
   git switch main
   git pull
   git branch -d feat/14-tel-and-map-links
   ```

## Things to know

- **Generated posts.** The workflow bot writes the files in `_posts/` on `main`. Do not commit generated posts from a feature branch, because they will conflict with the bot's commits. If you ran the script locally or in a Codespace, undo its output before committing:

  ```bash
  git restore _posts
  git clean -fd _posts
  ```

- **Sheet-only changes** (dropdowns, a Status column, the Google Form) happen in Google Sheets and do not need a branch.
- **Testing before merging.** Open a pull request and use the PR build check (once it exists). For a visual preview, open a GitHub Codespace on your branch and run:

  ```bash
  bundle install
  bundle exec jekyll serve --host 0.0.0.0
  ```

- **Deploying only from `main`.** Once the guards are added, the deploy workflow's jobs only run on `main`, so running it by hand from a branch will not publish anything.
- **Workflow changes.** The "Publish to site" button in the sheet always runs the workflow file on `main`, so edits to the deploy workflow only take effect after they are merged. Keep those pull requests small and watch the first run.

## Protecting `main`

Recommended settings (Settings > Rules > Rulesets, and Settings > General):

- Block force pushes and deletion of `main`.
- Require the PR build check to pass, once it exists.
- Turn on **Automatically delete head branches**.
- Do not require a pull request for every push to `main`. The workflow bot pushes generated posts directly to `main`, and that rule would make it fail unless the bot is allowed to bypass it.

## Avoid

- Long-lived branches such as `develop`, `staging`, or personal branches.
- Reusing a branch for a second task.
- Force-pushing to `main`.
- Committing directly to `main`, except to fix a broken live site quickly.