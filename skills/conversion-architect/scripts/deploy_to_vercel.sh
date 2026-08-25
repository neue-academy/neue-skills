#!/usr/bin/env bash
#
# Deploy an audited landing page to Vercel.
#
# The audit runs first and a failing page is never deployed. A landing-page skill that
# works in theory and breaks on the real `vercel` call is not finished, so this script
# also verifies the live URL responds before reporting success.
#
# Usage:
#   ./deploy_to_vercel.sh <dir-or-html> [--project NAME] [--preview] [--skip-audit]
#
# Token resolution, in order. Never hard-code a token in this file or commit one:
#   1. $VERCEL_TOKEN
#   2. .env / .env.local in the repo root (VERCEL_TOKEN=...)
#   3. `vercel login` session already on the machine
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
AUDIT="${SCRIPT_DIR}/audit_page.py"

TARGET=""
PROJECT="${VERCEL_PROJECT:-}"
SCOPE="${VERCEL_SCOPE:-}"
PROD=1
SKIP_AUDIT=0

die() { printf 'deploy: %s\n' "$1" >&2; exit 1; }
say() { printf '\033[1m›\033[0m %s\n' "$1"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --scope)   SCOPE="${2:-}"; shift 2 ;;
    --preview) PROD=0; shift ;;
    --skip-audit) SKIP_AUDIT=1; shift ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) die "unknown flag: $1" ;;
    *) TARGET="$1"; shift ;;
  esac
done

[[ -n "$TARGET" ]] || die "usage: deploy_to_vercel.sh <dir-or-html> [--project NAME] [--preview]"
[[ -e "$TARGET" ]] || die "no such path: $TARGET"
command -v vercel >/dev/null 2>&1 || die "vercel CLI not found. install: npm i -g vercel"

# --- token -----------------------------------------------------------------------------
if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  for candidate in "${REPO_ROOT}/.env.local" "${REPO_ROOT}/.env"; do
    if [[ -f "$candidate" ]]; then
      # shellcheck disable=SC2046
      export $(grep -E '^VERCEL_(TOKEN|PROJECT|SCOPE)=' "$candidate" | xargs) || true
    fi
  done
fi
TOKEN_ARGS=()
if [[ -n "${VERCEL_TOKEN:-}" ]]; then
  TOKEN_ARGS=(--token "$VERCEL_TOKEN")
  say "using VERCEL_TOKEN from environment (${#VERCEL_TOKEN} chars, not logged)"
else
  say "no VERCEL_TOKEN found — falling back to the local vercel login session"
fi
[[ -n "$SCOPE" ]] && TOKEN_ARGS+=(--scope "$SCOPE")

# --- stage -----------------------------------------------------------------------------
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/neue-deploy.XXXXXX")"
trap 'rm -rf "$BUILD_DIR"' EXIT

if [[ -d "$TARGET" ]]; then
  cp -R "$TARGET"/. "$BUILD_DIR"/
else
  cp "$TARGET" "$BUILD_DIR/index.html"
fi
[[ -f "$BUILD_DIR/index.html" ]] || die "no index.html in the deploy payload"

# --- audit gate ------------------------------------------------------------------------
if [[ "$SKIP_AUDIT" -eq 0 ]]; then
  say "auditing $(basename "$TARGET")"
  if ! python3 "$AUDIT" "$BUILD_DIR/index.html"; then
    die "page audit failed. fix the BLOCK findings above, or pass --skip-audit to override"
  fi
else
  say "audit skipped by flag"
fi

# --- deploy ----------------------------------------------------------------------------
DEPLOY_ARGS=(deploy "$BUILD_DIR" --yes "${TOKEN_ARGS[@]}")
[[ "$PROD" -eq 1 ]] && DEPLOY_ARGS+=(--prod)

if [[ -n "$PROJECT" ]]; then
  say "linking to project '$PROJECT'"
  ( cd "$BUILD_DIR" && vercel link --yes --project "$PROJECT" "${TOKEN_ARGS[@]}" >/dev/null )
fi

say "deploying$([[ "$PROD" -eq 1 ]] && echo ' to production' || echo ' as preview')"
DEPLOY_LOG="$(mktemp)"
if ! ( cd "$BUILD_DIR" && vercel "${DEPLOY_ARGS[@]}" ) >"$DEPLOY_LOG" 2>&1; then
  sed -E 's/(vcp_|vercel_)[A-Za-z0-9_-]+/[redacted]/g' "$DEPLOY_LOG" >&2
  rm -f "$DEPLOY_LOG"
  die "vercel deploy failed"
fi
DEPLOY_URL="$(grep -Eo 'https://[a-zA-Z0-9._-]+\.vercel\.app' "$DEPLOY_LOG" | tail -1)"
rm -f "$DEPLOY_LOG"
[[ -n "$DEPLOY_URL" ]] || die "deploy reported success but no URL was returned"

# --- verify ----------------------------------------------------------------------------
# Check the stable production alias before the deployment-specific URL. The alias is the
# link that gets shared, so it is the one that has to be serving.
CANDIDATES=()
if [[ "$PROD" -eq 1 && -n "$PROJECT" ]]; then
  CANDIDATES+=("https://${PROJECT}.vercel.app")
  [[ -n "$SCOPE" ]] && CANDIDATES+=("https://${PROJECT}-${SCOPE}.vercel.app")
fi
CANDIDATES+=("$DEPLOY_URL")

LIVE=""
PROTECTED=0
for candidate in "${CANDIDATES[@]}"; do
  for attempt in 1 2 3; do
    STATUS="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$candidate" || true)"
    if [[ "$STATUS" == "200" ]]; then LIVE="$candidate"; break; fi
    if [[ "$STATUS" =~ ^30 ]]; then
      LOCATION="$(curl -s -o /dev/null -D - --max-time 20 "$candidate" \
        | awk 'tolower($1)=="location:" {print $2}' | tr -d '\r')"
      if [[ "$LOCATION" == *"sso-api"* || "$LOCATION" == *"vercel.com/login"* ]]; then
        PROTECTED=1; break
      fi
    fi
    sleep $((attempt * 2))
  done
  [[ -n "$LIVE" ]] && break
done

if [[ -z "$LIVE" ]]; then
  printf 'deploy: checked %s\n' "${CANDIDATES[*]}" >&2
  if [[ "$PROTECTED" -eq 1 ]]; then
    die "the deployment is up but Vercel Deployment Protection is redirecting visitors to
     SSO login, so the page is not publicly reachable. Turn it off for this project:
     Vercel dashboard > project > Settings > Deployment Protection > Vercel Authentication
     > Disabled. A landing page has to be public."
  fi
  die "no candidate URL returned HTTP 200 — the deployment is not serving"
fi

printf '\n\033[1mLIVE\033[0m %s  (HTTP 200)\n' "$LIVE"
[[ "$LIVE" != "$DEPLOY_URL" ]] && printf '     deployment: %s\n' "$DEPLOY_URL"
exit 0
