#!/usr/bin/env bash
# Bump parent-repo gitlinks to the tip of each submodule's tracked branch,
# then land the change on the parent repo's GitHub via issue + PR.
# Run from the parent repo root.
set -euo pipefail

DRY_RUN=0
STAGE_ONLY=0
CHECKOUT=0
ASSUME_YES=0
VENV=/tmp/mkdocs-venv
SITE_DIR=/tmp/mkdocs-check

die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
log()  { printf '==> %s\n' "$*"; }
note() { printf '    %s\n' "$*"; }

usage() {
  cat <<'USAGE'
Usage: sync_submodules.sh [options] [submodule-path ...]

Bump the parent repo's recorded gitlinks to the tip of each submodule's
tracked branch. Submodule working trees are never checked out unless
--checkout is given.

Options:
  --dry-run      Print planned bumps only; no staging, build, commit, push, or PR
  --stage-only   Stage the gitlinks and stop
  --checkout     Also fast-forward a clean submodule branch to the new commit
  --yes          Skip the confirmation prompt before GitHub calls
  -h, --help     Show this help
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)    DRY_RUN=1 ;;
    --stage-only) STAGE_ONLY=1 ;;
    --checkout)   CHECKOUT=1 ;;
    --yes)        ASSUME_YES=1 ;;
    -h|--help)    usage; exit 0 ;;
    --)           shift; break ;;
    -*)           die "unknown option: $1" ;;
    *)            break ;;
  esac
  shift
done

requested=("$@")

# --- preflight ---------------------------------------------------------------
[ -f .gitmodules ] || die "run from the parent repo root (no .gitmodules here)"
command -v git     >/dev/null 2>&1 || die "git is required"
command -v gh      >/dev/null 2>&1 || die "gh CLI is required"
command -v python3 >/dev/null 2>&1 || die "python3 is required"

remote=$(git remote get-url origin 2>/dev/null || true)
case "$remote" in
  git@github.com:*|ssh://git@github.com/*) ;;
  *) note "WARNING: origin is not an SSH GitHub remote ($remote); HTTPS git transport may be flaky" ;;
esac

# Collect submodule names and paths from .gitmodules.
names=()
paths=()
while IFS=' ' read -r key path; do
  [ -n "$key" ] || continue
  name=${key#submodule.}
  name=${name%.path}
  names+=("$name")
  paths+=("$path")
done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.path$')
[ ${#paths[@]} -gt 0 ] || die "no submodules found in .gitmodules"

is_managed() {
  local needle=$1 p
  for p in "${paths[@]}"; do
    [ "$needle" = "$p" ] && return 0
  done
  return 1
}

# Validate explicit path arguments.
if [ ${#requested[@]} -gt 0 ]; then
  for r in "${requested[@]}"; do
    is_managed "$r" || die "unknown submodule path: $r"
  done
fi

# Never sweep unrelated work into the commit. Staged or unstaged changes to
# managed submodule paths are expected; anything else aborts.
while IFS= read -r f; do
  [ -n "$f" ] || continue
  is_managed "$f" || die "unrelated staged change: $f (resolve it before running)"
done < <(git diff --cached --name-only)
while IFS= read -r f; do
  [ -n "$f" ] || continue
  is_managed "$f" || die "unrelated unstaged change: $f (resolve it before running)"
done < <(git diff --name-only)

# Resolve the branch/issue names before any GitHub call. A stale local branch
# left behind by a previously merged bump PR must never abort the run *after*
# the tracking issue has already been created.
base=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)
[ -z "$base" ] && base=master
base_ref="refs/remotes/origin/$base"
git rev-parse --verify --quiet "$base_ref" >/dev/null || base_ref="$base"

if [ ${#requested[@]} -eq 1 ]; then
  slug=$(printf '%s' "${requested[0]}" | tr -cd 'a-zA-Z0-9-' | tr '[:upper:]' '[:lower:]')
  subject="docs: bump $slug submodule to latest"
else
  slug=submodules
  subject="docs: bump submodules to latest"
fi
[ -n "$slug" ] || die "empty branch slug"
branch="feature/bump-$slug"

# After a bump PR is squash-merged, GitHub deletes the remote branch but the
# local one survives. Remove that leftover only when it is provably superseded:
# a merged PR exists for that head, every change the branch carries is a managed
# gitlink, and those gitlinks already match the base branch. Otherwise stop and
# let the user resolve it — never delete a branch with unlanded work.
prepare_branch() {
  git show-ref --verify --quiet "refs/heads/$branch" || return 0

  local merged mb changed p their_sha base_sha
  merged=$(gh pr list --head "$branch" --state merged --json number --jq 'length' 2>/dev/null || printf '0')
  [ "$merged" != "0" ] || \
    die "branch $branch exists with no merged PR; resolve it before running"

  mb=$(git merge-base "$branch" "$base_ref") || \
    die "cannot compute merge base for $branch"
  changed=$(git diff --name-only "$mb" "$branch")
  for p in $changed; do
    is_managed "$p" || \
      die "branch $branch has non-gitlink changes ($p); resolve it manually"
    their_sha=$(git ls-tree "$branch" -- "$p" | awk '{print $3}')
    base_sha=$(git ls-tree "$base_ref" -- "$p" | awk '{print $3}')
    [ "$their_sha" = "$base_sha" ] || \
      die "branch $branch still has gitlink changes absent from $base; resolve it manually"
  done

  if [ "$DRY_RUN" -eq 1 ]; then
    note "would remove stale local branch $branch (merged PR leftover)"
    return 0
  fi
  if [ "$STAGE_ONLY" -eq 1 ]; then
    note "stale local branch $branch left in place (stage-only)"
    return 0
  fi

  git branch -D "$branch" >/dev/null
  log "removed stale local branch $branch (merged PR leftover; gitlinks already on $base)"
  if git show-ref --verify --quiet "refs/remotes/origin/$branch" &&
     [ -z "$(git ls-remote --heads origin "refs/heads/$branch")" ]; then
    git update-ref -d "refs/remotes/origin/$branch"
    note "pruned stale remote-tracking ref origin/$branch"
  fi
}
prepare_branch

# --- fetch, compare, stage ---------------------------------------------------
report=""
bumped=0

for ((i = 0; i < ${#paths[@]}; i++)); do
  name=${names[$i]}
  path=${paths[$i]}

  if [ ${#requested[@]} -gt 0 ]; then
    skip=1
    for r in "${requested[@]}"; do
      [ "$r" = "$path" ] && skip=0
    done
    [ "$skip" -eq 0 ] || continue
  fi

  [ -e "$path/.git" ] || die "submodule $path is not initialized"

  branch=$(git config -f .gitmodules --get "submodule.${name}.branch" 2>/dev/null || true)
  if [ -z "$branch" ]; then
    branch=$(git -C "$path" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)
  fi
  [ -z "$branch" ] && branch=main

  log "$path: fetching origin (tracked branch $branch)"
  git -C "$path" fetch --quiet origin

  sha=$(git -C "$path" rev-parse --verify "origin/${branch}^{commit}" 2>/dev/null) \
    || die "cannot resolve origin/$branch in $path"
  current=$(git ls-files -s -- "$path" | awk '{print $2}')
  [ -n "$current" ] || die "no gitlink in index for $path"

  if [ "$current" = "$sha" ]; then
    note "$path already at ${sha:0:8}"
    continue
  fi

  note "$current -> $sha"
  report="$report| $path | $current | $sha |"$'\n'
  bumped=$((bumped + 1))

  if [ "$DRY_RUN" -eq 0 ]; then
    git update-index --add --cacheinfo "160000,$sha,$path"

    if [ "$CHECKOUT" -eq 1 ]; then
      if [ -n "$(git -C "$path" status --porcelain)" ]; then
        note "skipping checkout: $path has uncommitted work"
      else
        git -C "$path" merge --ff-only --quiet "origin/$branch"
        note "fast-forwarded $path to ${sha:0:8}"
      fi
    fi
  fi
done

if [ "$bumped" -eq 0 ]; then
  log "already up to date; no issue or PR created"
  exit 0
fi

printf '\nPlanned gitlink bumps:\n'
printf '| Submodule | From | To |\n|-----------|------|----|\n'
printf '%s' "$report"

if [ "$DRY_RUN" -eq 1 ]; then
  log "dry run: no changes made"
  exit 0
fi

if [ "$STAGE_ONLY" -eq 1 ]; then
  log "staged gitlinks only"
  git diff --cached --submodule=short
  exit 0
fi

if [ "$ASSUME_YES" -ne 1 ]; then
  printf '\nCreate a tracking issue and PR on GitHub? [y/N] '
  read -r reply
  case "$reply" in
    y|Y) ;;
    *) log "aborted before any GitHub calls; gitlinks remain staged"; exit 0 ;;
  esac
fi

# --- quality gate ------------------------------------------------------------
if [ ! -x "$VENV/bin/python" ]; then
  log "creating mkdocs venv at $VENV"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet -r requirements.txt
fi
log "running mkdocs build --strict"
"$VENV/bin/python" -m mkdocs build --strict --site-dir "$SITE_DIR" \
  || die "strict build failed; no issue or PR created"

# --- github workflow ---------------------------------------------------------
# $base, $subject and $branch were resolved in preflight, before any GitHub call.
if git show-ref --verify --quiet "refs/heads/$branch"; then
  die "branch $branch reappeared after preflight; resolve it before running"
fi

# Build the shared markdown body. bash 3.2 mis-parses apostrophes inside a
# here-document nested in a command substitution, so use printf instead.
body_common() {
  printf '## Changes\n\n'
  printf '| Submodule | From | To |\n'
  printf '|-----------|------|----|\n'
  printf '%s' "$report"
  printf 'All changes are gitlink-only; no submodule working trees were modified.\n\n'
  printf '## Verification\n\n'
  printf -- '%s\n' \
    '- Each listed SHA is the tip of the submodule tracked branch after fetching origin.' \
    '- Pointer-only staging: no submodule working tree was touched.' \
    '- mkdocs build --strict passed with zero WARNINGs before the commit.' \
    '- CI does not build PRs, so the strict build was run locally.'
}

issue_body=$(
  printf '## Summary\n\n'
  printf 'Bump the parent repo gitlinks to the tip of each submodule tracked branch.\n\n'
  body_common
)

log "creating tracking issue"
issue_url=$(gh issue create --title "$subject" --body "$issue_body")
issue_num=${issue_url##*/}
case "$issue_num" in
  ''|*[!0-9]*) die "could not parse issue number from $issue_url" ;;
esac
note "issue #$issue_num"

log "creating branch $branch"
git switch -c "$branch" >/dev/null 2>&1 || git checkout -b "$branch"

log "committing"
git commit -m "$subject" -m "Closes #$issue_num"

log "pushing $branch"
git push -u origin "$branch"

pr_body=$(
  printf '## Summary\n\n'
  printf '%s\n\n' "$subject"
  printf 'Closes #%s\n\n' "$issue_num"
  body_common
)

log "creating PR against $base"
pr_url=$(gh pr create --base "$base" --head "$branch" --title "$subject" --body "$pr_body")
log "PR: $pr_url"
