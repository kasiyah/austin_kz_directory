# Contributing: branching policy

This repository is a Jekyll directory site published on GitHub Pages. Business posts are generated from a Google Sheet by `scripts/generate_posts.py` and deployed by GitHub Actions. This page explains how we use branches so the live site stays safe.

## The short version

- `main` is the only permanent branch.
- Every code change is made on a short-lived branch, merged through a pull request, and the branch is deleted afterwards.
- One issue = one branch = one pull request.
- Business listings are edited in the Google Sheet, not in branches.

## How the site gets updated

There are two separate paths:

| Kind of change | Where it happens | How it goes live |
|---|---|---|
| Business listings | Google Sheet | Click **Site > Publish to site** in the sheet. The workflow generates the posts, commits them to `main`, and deploys the site. |
| Site code (scripts, layouts, config, workflows) | Branch + pull request | Merge into `main`. A deploy starts automatically only if the merge changed `scripts/generate_posts.py` or `.github/workflows/auto_post_and_deploy.yml`. For any other change, publish by hand: **Site > Publish to site**, or **Actions > Run workflow** on `main`. |

## The workflow bot

The "workflow bot" is `github-actions[bot]`, the identity the deploy workflow uses to commit generated posts. Its commits are titled "Auto-generate business posts from Google Sheet CSV" and are pushed straight to `main` without a pull request. This is why `main` cannot require pull requests or status checks (see [Protecting `main`](#protecting-main)).

## Branches

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Production. The deploy workflow publishes from it, and the workflow bot commits generated posts to it. | Permanent |
| `<type>/<issue>-<description>` | One task, named as described below. | Deleted after merge |
| `dependabot/...` | Created automatically by Dependabot (once enabled). Leave the names as they are. | Deleted after merge |

We do not use `develop`, `staging`, or other long-lived branches. A pull request plus the PR build check is our safety step.

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
5. Wait for the **PR build check** and fix any failures. It runs the generator and builds the site without deploying, and its run summary lists which posts would change. You can also run it by hand: **Actions > PR build check > Run workflow**, then pick your branch.
6. Merge with **Squash and merge**. The branch is deleted automatically.
7. Publish if needed (see [How the site gets updated](#how-the-site-gets-updated)) and check that the workflow run on `main` succeeded.
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

- **Visual preview.** Open a GitHub Codespace on your branch and run:

  ```bash
  bundle install
  bundle exec jekyll serve --host 0.0.0.0
  ```

- **Deploying only from `main`.** The deploy workflow's jobs only run on `main`, so running it by hand from a branch will not publish anything.
- **Workflow changes.** The "Publish to site" button in the sheet always runs the workflow file on `main`, so edits to the deploy workflow only take effect after they are merged. Keep those pull requests small and watch the first run.

## Protecting `main`

Recommended settings (Settings > Rules > Rulesets, and Settings > General):

- Block force pushes and deletion of `main`.
- Turn on **Automatically delete head branches**.
- Check that the PR build check is green before merging. GitHub cannot enforce it here, because the workflow bot pushes directly to `main`.
- Do **not** turn on any of these rules for `main`, because each one makes the workflow bot's push fail: require a pull request, require status checks, restrict updates, require signed commits.

## Troubleshooting

- **"Commit and push posts" fails with "push declined due to repository rule violations."** A rule on `main` is blocking the workflow bot. Open Settings > Rules > Rulesets and turn off the rules listed above.
- **The sheet's Publish button reports a failure.** The GitHub token saved in the Apps Script properties has probably expired or lost access. Create a new token and update the `GITHUB_TOKEN` property.

## Avoid

- Long-lived branches such as `develop`, `staging`, or personal branches.
- Reusing a branch for a second task.
- Force-pushing to `main`.
- Committing directly to `main`, except to fix a broken live site quickly. The workflow bot's post commits are the only routine exception.