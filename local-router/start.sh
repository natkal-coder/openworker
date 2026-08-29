#!/usr/bin/env bash
# Local model gateway (LiteLLM proxy) on :4000 — the `local-router` provider's endpoint.
# Models/aliases live in litellm.yaml next to this script. Log: ~/.config/coworker/local-router.log
set -euo pipefail
PORT="${LOCAL_ROUTER_PORT:-4000}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="$HERE/litellm.yaml"
LOG="${XDG_CONFIG_HOME:-$HOME/.config}/coworker/local-router.log"
BIN="$(command -v litellm || true)"
[ -x "$HOME/.local/bin/litellm" ] && BIN="$HOME/.local/bin/litellm"
[ -n "$BIN" ] || { echo "ERROR: litellm not found — run: uv tool install --python 3.12 'litellm[proxy]'"; exit 1; }
mkdir -p "$(dirname "$LOG")"
lsof -ti:"$PORT" | xargs -r kill || true
sleep 1
nohup "$BIN" --config "$CFG" --host 127.0.0.1 --port "$PORT" > "$LOG" 2>&1 < /dev/null &
for _ in $(seq 1 60); do
  if curl -s --max-time 2 "http://127.0.0.1:$PORT/health/liveliness" | grep -q -i alive; then
    echo "local-router up: http://127.0.0.1:$PORT/v1  (key: sk-local-router)"
    exit 0
  fi
  sleep 1
done
echo "ERROR: router did not come up — see $LOG"; tail -20 "$LOG"; exit 1
