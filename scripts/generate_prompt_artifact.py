#!/usr/bin/env python3
"""Generate condensed prompt artifacts from a transcript.

Supports two modes:
- dry-run: create assembled prompt packages without calling an LLM
- ollama: call a local Ollama endpoint to generate the final artifacts
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = BASE_DIR / "prompts"
PROFILES_DIR = BASE_DIR / "config" / "profiles"

PROFILE_MAP = {
    "full-context": {
        "prompt_file": PROMPTS_DIR / "universal_full_context.txt",
        "exclude_keywords": [],
        "description": "Preserve broad context when it influenced the solution.",
    },
    "technical-only": {
        "prompt_file": PROMPTS_DIR / "technical_context_only.txt",
        "exclude_keywords": [
            "travel",
            "cruise",
            "vacation",
            "family",
            "road trip",
            "roadtrip",
            "learning plan",
            "radio",
            "parenting",
            "estate planning",
        ],
        "description": "Filter out non-technical content unless it directly affects implementation.",
    },
}

OUTPUT_REQUEST = textwrap.dedent(
    """
    Produce three outputs with these exact section headers:
    === MASTER PROMPT ===
    === LLM-OPTIMIZED VERSION ===
    === REPO-READY README ===

    The master prompt must be a single dense instruction block in sentence form.
    The LLM-optimized version may use minimal headers but should remain concise and execution-oriented.
    The repo-ready README should include overview, architecture summary, capabilities, deliverables, and suggested folder structure.
    """
).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate prompt artifacts from transcripts.")
    parser.add_argument("--input", required=True, help="Path to transcript file (.txt, .md, .json).")
    parser.add_argument("--profile", choices=PROFILE_MAP.keys(), default="technical-only")
    parser.add_argument("--mode", choices=["dry-run", "ollama"], default="dry-run")
    parser.add_argument("--model", default="llama3.1:8b", help="Local Ollama model name.")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434", help="Base URL for Ollama API.")
    parser.add_argument("--output-dir", default=str(BASE_DIR / "output"))
    parser.add_argument("--title", default="conversation")
    return parser.parse_args()


def read_input(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, indent=2)
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def filter_text(text: str, profile_name: str) -> str:
    profile = PROFILE_MAP[profile_name]
    if profile_name != "technical-only":
        return text

    kept = []
    for block in re.split(r"\n\n+", text):
        lower = block.lower()
        if any(keyword in lower for keyword in profile["exclude_keywords"]):
            tech_signal = any(
                token in lower
                for token in [
                    "docker",
                    "ansible",
                    "kubernetes",
                    "ssh",
                    "network",
                    "server",
                    "linux",
                    "vm",
                    "storage",
                    "script",
                    "yaml",
                    "compose",
                    "api",
                    "repo",
                    "prompt",
                    "automation",
                    "ollama",
                    "gpu",
                ]
            )
            if not tech_signal:
                continue
        kept.append(block)
    return "\n\n".join(kept).strip()


def build_user_payload(transcript: str, profile_name: str) -> str:
    return textwrap.dedent(
        f"""
        Conversation profile: {profile_name}
        Profile description: {PROFILE_MAP[profile_name]['description']}

        Source transcript follows.
        --- BEGIN TRANSCRIPT ---
        {transcript}
        --- END TRANSCRIPT ---

        {OUTPUT_REQUEST}
        """
    ).strip()


def ollama_generate(system_prompt: str, user_prompt: str, model: str, ollama_url: str) -> str:
    url = ollama_url.rstrip("/") + "/api/generate"
    payload = json.dumps(
        {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to call Ollama endpoint {url}: {exc}") from exc
    return body.get("response", "").strip()


def split_sections(text: str) -> Dict[str, str]:
    sections = {
        "master_prompt": "",
        "llm_optimized": "",
        "repo_ready_readme": "",
    }
    patterns = {
        "master_prompt": r"=== MASTER PROMPT ===\s*(.*?)(?=== LLM-OPTIMIZED VERSION ===|\Z)",
        "llm_optimized": r"=== LLM-OPTIMIZED VERSION ===\s*(.*?)(?=== REPO-READY README ===|\Z)",
        "repo_ready_readme": r"=== REPO-READY README ===\s*(.*)\Z",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.S)
        if match:
            sections[key] = match.group(1).strip()
    return sections


def dry_run_content(system_prompt: str, user_payload: str) -> Tuple[str, Dict[str, str]]:
    synthetic = textwrap.dedent(
        f"""
        === MASTER PROMPT ===
        {system_prompt}

        Reconstruct the source transcript into a condensed, self-contained prompt package using the provided conversation payload and preserve all material technical and contextual decisions.

        === LLM-OPTIMIZED VERSION ===
        Use the system instructions and transcript payload below to generate a compact master prompt, an execution-optimized version, and a repo-ready implementation summary. Resolve duplication, preserve decisions, and remove noise.

        === REPO-READY README ===
        # Generated Prompt Artifact

        This dry-run output shows the request package that would be sent to a local model. The final implementation should summarize the source transcript, preserve important decisions, and emit the three required outputs.
        """
    ).strip()
    return synthetic, split_sections(synthetic)


def write_outputs(output_dir: Path, title: str, profile: str, mode: str, raw_text: str, sections: Dict[str, str]) -> None:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_dir / f"{title}-{profile}-{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "full_output.txt").write_text(raw_text + "\n", encoding="utf-8")
    (run_dir / "master_prompt.txt").write_text(sections.get("master_prompt", "") + "\n", encoding="utf-8")
    (run_dir / "llm_optimized.txt").write_text(sections.get("llm_optimized", "") + "\n", encoding="utf-8")
    (run_dir / "README.generated.md").write_text(sections.get("repo_ready_readme", "") + "\n", encoding="utf-8")
    metadata = {
        "title": title,
        "profile": profile,
        "mode": mode,
        "created_at": dt.datetime.now().isoformat(),
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Artifacts written to: {run_dir}")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    transcript = normalize_text(read_input(input_path))
    filtered_transcript = filter_text(transcript, args.profile)
    system_prompt = PROFILE_MAP[args.profile]["prompt_file"].read_text(encoding="utf-8").strip()
    user_payload = build_user_payload(filtered_transcript, args.profile)

    if args.mode == "dry-run":
        raw_text, sections = dry_run_content(system_prompt, user_payload)
    else:
        raw_text = ollama_generate(system_prompt, user_payload, args.model, args.ollama_url)
        sections = split_sections(raw_text)

    write_outputs(output_dir, args.title, args.profile, args.mode, raw_text, sections)
    return 0


if __name__ == "__main__":
    sys.exit(main())
