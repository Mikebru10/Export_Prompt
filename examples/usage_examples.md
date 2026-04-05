# Usage Examples

## Dry-run, technical-only

```bash
./scripts/run_local_workflow.sh examples/sample_input.md technical-only dry-run
```

## Full-context against local Ollama

```bash
OLLAMA_MODEL=llama3.1:8b ./scripts/run_local_workflow.sh examples/sample_input.md full-context ollama
```

## Convert JSON export to Markdown first

```bash
python3 scripts/transcript_to_markdown.py --input exported-chat.json --output exported-chat.md
./scripts/run_local_workflow.sh exported-chat.md technical-only ollama
```
