#!/usr/bin/env bash
# Generate a short-lived Dremio token without exposing credentials or token output.

set -euo pipefail
umask 077

usage() {
  cat >&2 <<'USAGE'
Usage: get_dremio_token.sh [--output PATH]

Credentials are read interactively. The token is written to PATH atomically
with mode 0600 (default: ~/.secrets/dremio_pat); it is never printed.
USAGE
}

DREMIO_HOST="${DREMIO_HOST:-lakehouse-1.jgi.lbl.gov}"
DREMIO_PORT="${DREMIO_PORT:-9047}"
DREMIO_LOGIN_URL="https://${DREMIO_HOST}:${DREMIO_PORT}/apiv2/login"
OUTFILE="${HOME}/.secrets/dremio_pat"

while (($#)); do
  case "$1" in
    --output)
      if (($# < 2)) || [[ -z "$2" || "$2" == "-" ]]; then
        echo "Error: --output requires a file path" >&2
        usage
        exit 2
      fi
      OUTFILE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: credentials are read interactively and are not accepted as arguments" >&2
      usage
      exit 2
      ;;
  esac
done

if ! command -v curl >/dev/null 2>&1; then
  echo "Error: curl is required" >&2
  exit 1
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required for safe JSON handling" >&2
  exit 1
fi

IFS= read -r -p "Username: " USERNAME
IFS= read -r -s -p "Password: " PASSWORD
printf '\n' >&2
if [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
  echo "Error: username and password cannot be empty" >&2
  exit 1
fi

PAYLOAD_FILE=$(mktemp)
RESPONSE_FILE=$(mktemp)
TOKEN_TMP=""
cleanup() {
  rm -f -- "$PAYLOAD_FILE" "$RESPONSE_FILE"
  if [[ -n "$TOKEN_TMP" ]]; then
    rm -f -- "$TOKEN_TMP"
  fi
}
trap cleanup EXIT HUP INT TERM
chmod 600 "$PAYLOAD_FILE" "$RESPONSE_FILE"

# Send credentials over stdin so shell quoting cannot change the JSON payload and
# neither credential appears in the Python process arguments.
printf '%s\n%s' "$USERNAME" "$PASSWORD" |
  uv run --no-project python -c \
    'import json, sys; username = sys.stdin.readline().rstrip("\n"); password = sys.stdin.read(); json.dump({"userName": username, "password": password}, sys.stdout)' \
    >"$PAYLOAD_FILE"
unset USERNAME PASSWORD

CURL_ARGS=(
  --silent
  --show-error
  --write-out "%{http_code}"
  --output "$RESPONSE_FILE"
  --request POST
  --header "Content-Type: application/json"
  --data-binary "@$PAYLOAD_FILE"
)
if [[ -n "${DREMIO_CA_BUNDLE:-}" ]]; then
  CURL_ARGS+=(--cacert "$DREMIO_CA_BUNDLE")
fi

HTTP_CODE=$(curl "${CURL_ARGS[@]}" "$DREMIO_LOGIN_URL")
if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Error: authentication failed (HTTP $HTTP_CODE)" >&2
  exit 1
fi

if ! TOKEN=$(uv run --no-project python -c \
  'import json, sys; token = json.load(sys.stdin).get("token"); assert isinstance(token, str) and token.strip(); print(token.strip())' \
  <"$RESPONSE_FILE" 2>/dev/null); then
  echo "Error: authentication response did not contain a token" >&2
  exit 1
fi

OUTDIR=$(dirname -- "$OUTFILE")
mkdir -p -- "$OUTDIR"
TOKEN_TMP=$(mktemp "$OUTDIR/.dremio_pat.tmp.XXXXXX")
chmod 600 "$TOKEN_TMP"
printf '%s\n' "$TOKEN" >"$TOKEN_TMP"
unset TOKEN
mv -f -- "$TOKEN_TMP" "$OUTFILE"
TOKEN_TMP=""
chmod 600 "$OUTFILE"

echo "Token stored in $OUTFILE" >&2
