---
name: submodule-sync
description: "Use when a git submodule's tracked branch has new commits but the parent repo still records an older gitlink, or when the user asks to bump submodules to latest and sync the pointer into the parent repository. Triggers: submodule behind origin, stale gitlink, git submodule status divergence after a remote push, update submodules to latest, sync submodule pointer to parent git."
author: melodypapa
license: MIT
repository: https://github.com/melodypapa/uncertainty
keywords: [git, submodule, gitlink, sync, automation]
version: "1.0.0"
product-version: "1.0.0"
spec-version: "1.0.0"
---

# Submodule Sync

**Core principle:** Bump the parent repo's gitlink, never the submodule's working tree. A submodule often holds uncommitted work, and checking out inside it can destroy that work.

## When to Use

- A submodule has new commits on its tracked branch and the parent repo still records the old commit
- The user asks to update a submodule to latest and land the pointer change in the parent repo
- `git submodule status` shows divergence after commits were pushed to the submodule's remote

**NOT for:** Committing content inside a submodule (that repo has its own workflow), or a plain `git submodule update` that only refreshes a checkout without changing the parent's recorded commit.

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| 0 | `scripts/sync_submodules.sh --dry-run` | Preview bumps; no state change |
| 1 | `scripts/sync_submodules.sh` | Full workflow: stage, gate, issue, branch, commit, push, PR |
| 2 | `git diff --cached --submodule=short` | Review exact old-to-new SHAs |
| 3 | `git submodule status` | Confirm expected divergence |

Run the script from the parent repo root. Pass one or more submodule paths to limit scope; with no paths it checks every entry in `.gitmodules`.

**Always run `--dry-run` first and show the user the plan. Get explicit confirmation before the real run, because it creates a GitHub issue and PR.**

## Script Options

| Flag | Effect |
|------|--------|
| `--dry-run` | Compute and print bumps only; skips staging, build, commit, push, and all GitHub calls |
| `--stage-only` | Stage the gitlinks and stop; no commit, push, or PR |
| `--checkout` | Also fast-forward a clean submodule branch to the new commit |
| `--yes` | Skip the confirmation prompt before GitHub calls |
| `-h`, `--help` | Show help |

Without `--checkout` the submodule checkout stays where it was, so `git submodule status` shows `+` for a bumped submodule until the user runs `git submodule update` after the PR merges. This is expected and safe.

## Workflow

1. **Preflight** — verify repo root, `.gitmodules`, `gh`, and that staged changes are limited to managed submodule gitlinks. Abort otherwise.
2. **Refresh and compare** — update each submodule's remote-tracking refs, resolve its tracked branch (the `.gitmodules` branch key, else the remote HEAD branch, else `main`), and compare the branch tip with the gitlink currently in the **index**, not `HEAD`.
3. **Stage** — write the new gitlink with `git update-index --add --cacheinfo 160000,<sha>,<path>`. This does not require the commit object in the parent object database and does not touch the submodule working tree.
4. **Early exit** — if every submodule is already current, report "already up to date" and stop. No issue or PR is created.
5. **Quality gate** — run the MkDocs strict build, recreating `/tmp/mkdocs-venv` from `requirements.txt` when missing. Stop immediately on any WARNING. CI does not build PRs, so this local gate is the only one.
6. **Issue** — create an English tracking issue and capture its number.
7. **Branch** — create `feature/bump-<slug>`; never commit on the protected default branch.
8. **Commit** — `docs: bump <submodule> submodule to latest` with `Closes #N` in the body. No co-work attribution.
9. **Push** — push the branch over the SSH remote; HTTPS git transport is unreliable in this project.
10. **PR** — open an English PR against the default branch with a summary, a per-submodule SHA table, and a verification list including the strict-build result.

## Red Flags - STOP

- Running `git submodule update --remote`, `git checkout`, or `git merge` inside a submodule with uncommitted work
- Bumping to a commit that is not the tip of the tracked branch
- Committing the gitlink directly on `master` or `main`
- Skipping the strict build, or passing `--no-verify`
- Creating an issue or PR when no gitlink actually changed
- Hardcoding credentials instead of using `gh` auth and the SSH remote
- Adding Co-Authored-By or any AI attribution to commits, issues, or PRs

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `git add <path>` after a remote push, which stages the old checkout instead of the new tip | Use `git update-index --cacheinfo` with the fetched tip |
| Assuming the tracked branch is `main` | Resolve the `.gitmodules` branch key, then remote HEAD, then fall back to `main` |
| Comparing against `HEAD` instead of the index | The index may already hold a staged bump; compare `git ls-files -s` |
| Treating a dirty submodule as an error | Pointer-only staging is designed to work with dirty working trees |
| Expecting `git submodule status` to be clean right after a bump | The `+` marker is expected until a later `git submodule update` |
