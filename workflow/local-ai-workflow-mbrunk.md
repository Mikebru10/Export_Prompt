# Local AI Workflow (MBrunk Homelab)

## Deployment target

Primary execution host:
- vUbtDoc-Infra-Crt-Prod-N01.mbrunk.net

## Storage layout

/mnt/docker_nfs/docker/vUbtDoc-Infra-Crt-Prod-N01/prompt-optimizer/
├── input/
├── output/
├── archive/
└── repo/

## Execution model

Centralized prompt processing node. Transcripts are dropped into input, processed, and archived.

## Example execution

run-prompt-optimizer /mnt/docker_nfs/docker/vUbtDoc-Infra-Crt-Prod-N01/prompt-optimizer/input/chat.md technical-only ollama

## Cron example

*/15 * * * * /usr/local/bin/run-mbrunk-batch

## Ollama integration

export OLLAMA_URL=http://REPLACE_WITH_YOUR_OLLAMA_HOST:11434

## Notes

- Designed for technical conversations
- Uses existing NFS-backed storage conventions
