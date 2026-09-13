#!/bin/zsh
set -e
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  print 'Project environment is missing. Ask Codex to restore the pinned local environment.'
  exit 1
fi
if ! curl --silent --fail --max-time 3 http://127.0.0.1:1234/v1/models >/dev/null; then
  "$HOME/.lmstudio/bin/lms" server start --bind 127.0.0.1 --port 1234
fi
if ! curl --silent --fail --max-time 3 http://127.0.0.1:1234/v1/models | .venv/bin/python -c 'import sys,json;sys.exit(not any(m["id"]=="fly-regulator-llm" for m in json.load(sys.stdin)["data"]))'; then
  "$HOME/.lmstudio/bin/lms" load qwen3.5-4b --identifier fly-regulator-llm --context-length 4096 --gpu max -y
fi
print 'Open http://127.0.0.1:8765 in your browser. Ctrl+C stops the interface.'
exec .venv/bin/python web/server.py
