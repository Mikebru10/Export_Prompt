# Local AI Workflow

This workflow is intended for private transcript processing inside a homelab, workstation, or single-host Docker environment.

## Goal

Convert saved AI chat transcripts into reusable prompt artifacts without sending the conversation to external hosted models.

## Recommended architecture

A local host stores exported transcripts under an input directory such as `/mnt/docker_nfs/docker/prompt-optimizer/input`. A local LLM runtime such as Ollama serves an inference API on the same host or on a nearby trusted server. The toolkit reads each transcript, filters it according to the selected profile, submits the assembled request to the local model, and writes the results into a timestamped output directory. Outputs can then be committed to GitHub, copied to a notes system, or reused directly in future AI chats.

## Suggested host types

- Mac mini for quiet local usage with smaller models
- Ubuntu VM for always-on homelab processing
- GPU server for larger local models and faster batch generation

## Example directory layout

```text
/mnt/docker_nfs/docker/prompt-optimizer/
├── input/
├── output/
├── archive/
└── repo/
```

## Basic workflow

1. Export or save a chat transcript as Markdown, text, or JSON.
2. Place the transcript in the input directory.
3. Run the wrapper script manually, from cron, or from a systemd timer.
4. Review generated outputs in the output directory.
5. Optionally archive the original transcript and commit the resulting prompt artifacts to GitHub.

## Example command

```bash
run-prompt-optimizer /mnt/docker_nfs/docker/prompt-optimizer/input/chat-2026-03-31.md technical-only ollama
```

## Suggested automation patterns

### Cron example

```cron
15 * * * * /usr/local/bin/find /mnt/docker_nfs/docker/prompt-optimizer/input -maxdepth 1 -type f -name '*.md' -print0 | xargs -0 -I{} /usr/local/bin/run-prompt-optimizer "{}" technical-only ollama
```

### systemd timer pattern

Use a systemd service that scans an input directory and invokes `run-prompt-optimizer` for new files, then moves processed files into an archive directory.

## Local model guidance

Use smaller models for fast draft summarization and larger models for higher-fidelity prompt reconstruction. For technical conversations, instruction-tuned models that follow formatting constraints well are usually more reliable than purely general-purpose chat models.
