#!/usr/bin/env python3
"""Normalize a simple JSON chat export into Markdown.

Expected input shapes:
- list[dict] with keys role/content
- dict with a top-level messages list
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    messages = data["messages"] if isinstance(data, dict) and "messages" in data else data
    lines = []
    for item in messages:
        role = str(item.get("role", "unknown")).upper()
        content = item.get("content", "")
        if isinstance(content, list):
            content = "\n".join(str(x) for x in content)
        lines.append(f"## {role}\n\n{content}\n")
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
