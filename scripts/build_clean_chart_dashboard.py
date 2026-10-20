#!/usr/bin/env python3
"""Locate the maintained training page without generating a second template."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_INDEX = ROOT / "our-project/dashboard/index.html"


def main():
    page = CANONICAL_INDEX.read_text(encoding="utf-8")
    print(f"Training dashboard: {CANONICAL_INDEX} ({len(page.splitlines())} lines)")
    return CANONICAL_INDEX


if __name__ == "__main__":
    main()
