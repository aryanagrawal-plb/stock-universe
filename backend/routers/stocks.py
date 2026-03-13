"""Stock data API router."""

import json
from pathlib import Path

from fastapi import APIRouter

from models.schemas import Stock

router = APIRouter(tags=["stocks"])

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "universe_master.json"

_stocks_cache: list[dict] | None = None


def _load_stocks() -> list[dict]:
    """Load stock records from the JSON data file (cached after first call)."""
    global _stocks_cache
    if _stocks_cache is None:
        with open(DATA_PATH, encoding="utf-8") as f:
            _stocks_cache = json.load(f)
    return _stocks_cache


@router.get("/stocks", response_model=list[Stock], response_model_by_alias=False)
async def get_stocks() -> list[dict]:
    """Return all stock data from the universe master dataset."""
    return _load_stocks()
