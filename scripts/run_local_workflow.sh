#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INPUT_PATH="${1:-}"
PROFILE="${2:-technical-only}"
MODE="${3:-dry-run}"
MODEL="${OLLAMA_MODEL:-llama3.1:8b}"
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"

if [[ -z "$INPUT_PATH" ]]; then
  echo "Usage: $0 <transcript-file> [profile] [mode]"
  exit 1
fi

python3 "$ROOT_DIR/scripts/generate_prompt_artifact.py" \
  --input "$INPUT_PATH" \
  --profile "$PROFILE" \
  --mode "$MODE" \
  --model "$MODEL" \
  --ollama-url "$OLLAMA_URL" \
  --output-dir "$ROOT_DIR/output" \
  --title "$(basename "$INPUT_PATH" | sed 's/\.[^.]*$//')"
