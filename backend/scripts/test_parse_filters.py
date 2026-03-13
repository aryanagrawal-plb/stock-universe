#!/usr/bin/env python3
"""Interactive script to test the NLP-to-filters pipeline.

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/test_parse_filters.py

Requires DEEPSEEK_API_KEY in the environment or in backend/.env.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.agent import parse_filters_from_nl, summarise_filters  # noqa: E402

SAMPLE_QUERIES: list[str] = [
    "Show me US technology stocks with PE ratio under 30 and dividend yield above 2%",
    "I want cheap Japanese stocks in the energy sector",
    "Find large-cap European healthcare companies with high Sharpe ratio",
    "AAPL",
    "Stocks on NYSE with market cap over 100 billion",
    "Give me high dividend stocks from Australia and Canada",
]


async def run_single(query: str) -> None:
    """Parse a single query and print results."""
    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
    print("-" * 70)

    filters = await parse_filters_from_nl(query)
    data = filters.model_dump(exclude_none=True)

    print("FILTERS (JSON):")
    print(json.dumps(data, indent=2))
    print()
    print(f"SUMMARY: {summarise_filters(filters)}")


async def main() -> None:
    """Run sample queries or accept interactive input."""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        await run_single(query)
        return

    print("Stock Universe — NLP Filter Parser")
    print("Running sample queries...\n")

    for query in SAMPLE_QUERIES:
        await run_single(query)

    print(f"\n{'='*70}")
    print("\nInteractive mode — type a query (or 'quit' to exit):\n")
    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query or query.lower() in ("quit", "exit", "q"):
            break
        await run_single(query)


if __name__ == "__main__":
    asyncio.run(main())
