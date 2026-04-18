#!/usr/bin/env python3
"""Build seed-index.json and JSON card sidecars from vault/cards/*.md.

Reads YAML frontmatter from each markdown card note in vault/cards/.
Generates:
  - seed-index.json at repo root (federation-ready)
  - cards/{seed}.json at repo root (federation-ready)

Usage: python scripts/build.py

Requires only Python stdlib. No dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_CARDS = REPO_ROOT / "vault" / "cards"
OUTPUT_CARDS = REPO_ROOT / "cards"
SEED_INDEX = REPO_ROOT / "seed-index.json"

REQUIRED_FIELDS = ("seed", "incantation", "name", "agent_id")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML-ish frontmatter from a markdown file.

    Supports the subset of YAML we use: scalars, quoted strings, lists.
    Returns (metadata_dict, body_after_frontmatter).
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]

    meta: dict[str, object] = {}
    for line in raw.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        meta[key] = _parse_value(value)
    return meta, body


def _parse_value(value: str) -> object:
    """Parse a single YAML scalar (string, int, list)."""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(item.strip()) for item in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    return value


def build_card_payload(meta: dict, body: str, source_path: Path) -> dict:
    """Construct the federation-shaped JSON for a single card."""
    return {
        "version": "1.1.2",
        "seed": str(meta["seed"]),
        "incantation": meta["incantation"],
        "name": meta["name"],
        "agent_id": meta["agent_id"],
        "source": meta.get("source", "obsidian-binder"),
        "tags": meta.get("tags", []),
        "created": meta.get("created"),
        "notes_excerpt": _excerpt(body),
        "_meta": {
            "owner": "obsidian-binder",
            "source_file": f"vault/cards/{source_path.name}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def _excerpt(body: str, max_chars: int = 280) -> str:
    """First non-heading paragraph of the markdown body, trimmed."""
    text = body.strip()
    for paragraph in text.split("\n\n"):
        cleaned = paragraph.strip()
        if cleaned and not cleaned.startswith("#"):
            single = re.sub(r"\s+", " ", cleaned)
            if len(single) > max_chars:
                return single[: max_chars - 1] + "…"
            return single
    return ""


def main() -> int:
    if not VAULT_CARDS.is_dir():
        print(f"No vault/cards/ directory at {VAULT_CARDS}", file=sys.stderr)
        return 1

    OUTPUT_CARDS.mkdir(exist_ok=True)
    seeds: dict[str, str] = {}
    errors: list[str] = []
    cards_built = 0

    for md_path in sorted(VAULT_CARDS.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        missing = [f for f in REQUIRED_FIELDS if f not in meta]
        if missing:
            errors.append(f"{md_path.name}: missing frontmatter fields {missing}")
            continue

        seed = str(meta["seed"])
        payload = build_card_payload(meta, body, md_path)
        out_path = OUTPUT_CARDS / f"{seed}.json"
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        seeds[seed] = f"cards/{seed}.json"
        cards_built += 1

    if errors:
        for e in errors:
            print(f"WARN: {e}", file=sys.stderr)

    index = {
        "version": "1.1.2",
        "owner": "obsidian-binder",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "card_count": len(seeds),
        "seeds": seeds,
    }
    SEED_INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Built {cards_built} cards → seed-index.json + cards/*.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
