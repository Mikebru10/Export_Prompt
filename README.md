# Prompt Optimizer Toolkit

A portable toolkit for turning long ChatGPT or AI conversations into compact, reusable prompts and implementation artifacts. This repo is designed for three use cases: direct manual prompt cleanup, automated transcript-to-prompt generation, and deployment into a local homelab or automation environment.

The toolkit ships with two conversation profiles:

1. **full-context**: keeps broad context that may include technical, planning, and adjacent conversational details when they materially affected the final design.
2. **technical-only**: aggressively filters non-technical context so the resulting prompt is focused on coding, homelab, infrastructure, networking, deployment, automation, and systems design work.

## What it produces

Given a chat transcript or conversation log, the workflow can generate:

- a single condensed master prompt in plain text
- an LLM-optimized execution prompt
- a repo-ready README-style implementation brief
- optional metadata files for traceability and review

## Repository layout

```text
prompt-optimizer-toolkit/
├── README.md
├── prompts/
│   ├── universal_full_context.txt
│   └── technical_context_only.txt
├── scripts/
│   ├── generate_prompt_artifact.py
│   ├── run_local_workflow.sh
│   └── transcript_to_markdown.py
├── config/
│   └── profiles/
│       ├── full_context.yaml
│       └── technical_only.yaml
├── ansible/
│   ├── deploy-prompt-optimizer.yml
│   └── roles/
│       └── prompt_optimizer/
│           ├── tasks/
│           │   └── main.yml
│           ├── templates/
│           │   ├── prompt-optimizer.env.j2
│           │   └── run-prompt-optimizer.sh.j2
│           └── files/
├── workflow/
│   ├── local-ai-workflow.md
│   └── ollama-systemd-service.example
├── examples/
│   ├── sample_input.md
│   └── usage_examples.md
└── output/
```

## High-level architecture

A transcript is provided to the Python generator either as Markdown, plain text, or lightly structured JSON. The generator normalizes the transcript, applies the selected profile, composes a system prompt plus profile-specific instructions, and optionally sends the full request to a local LLM endpoint such as Ollama. The generated outputs are then written to timestamped files under `output/`.

The automation layer can be deployed with Ansible. The role installs Python, copies the toolkit to a target host, places a runtime environment file, and installs a wrapper script that can be called manually, from cron, from systemd timers, or from other orchestration tools.

## Intended deployment patterns

### Manual local use
Run the generator against a saved transcript and create prompt artifacts in one command.

### Homelab batch processing
Drop transcripts into an input directory and run the wrapper from cron or a systemd timer to process new files automatically.

### AI workstation integration
Pair the toolkit with a local LLM runtime such as Ollama on a Mac mini, Linux VM, or GPU server, then use it to produce prompt artifacts without sending transcripts to cloud services.

## Quick start

### 1. Prepare a transcript
Save a conversation to a file such as `conversation.md`, `conversation.txt`, or simple JSON.

### 2. Run the generator in dry-run mode

```bash
python3 scripts/generate_prompt_artifact.py \
  --input examples/sample_input.md \
  --profile technical-only \
  --mode dry-run \
  --output-dir output
```

### 3. Run against a local Ollama endpoint

```bash
python3 scripts/generate_prompt_artifact.py \
  --input examples/sample_input.md \
  --profile full-context \
  --mode ollama \
  --model llama3.1:8b \
  --ollama-url http://127.0.0.1:11434 \
  --output-dir output
```

## Profiles

### full-context
Use when you want the condensed prompt to preserve the broader design rationale of the conversation, even if some details came from adjacent planning topics.

### technical-only
Use when the conversation is mainly about infrastructure, coding, homelab, network design, deployment, automation, troubleshooting, architecture, or software build work and you want non-technical context removed.

## Ansible deployment

Example:

```bash
ansible-playbook -i inventory.ini ansible/deploy-prompt-optimizer.yml
```

Set host variables such as:

```ini
[prompt_optimizer_hosts]
10.19.1.171

[prompt_optimizer_hosts:vars]
prompt_optimizer_install_dir=/opt/prompt-optimizer
prompt_optimizer_user=mike
prompt_optimizer_group=mike
prompt_optimizer_ollama_url=http://127.0.0.1:11434
prompt_optimizer_default_model=llama3.1:8b
```

## Suggested integration points

- GitHub repo for versioning prompt profiles and scripts
- Ansible for installation and updates across Linux hosts
- Cron or systemd timers for scheduled transcript processing
- Ollama for private local LLM inference
- Shared NFS/SMB storage if multiple hosts will feed transcripts into the same processing pipeline

## Notes

This toolkit intentionally focuses on prompt reconstruction and architecture summarization, not on perfect transcript parsing for every export format. The supplied scripts are robust enough for plain-text and Markdown conversations and can be extended for platform-specific JSON exports.
