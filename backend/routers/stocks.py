"""Stock data API router."""

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query

from models.schemas import Stock

router = APIRouter(tags=["stocks"])

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "stocks.json"


def _load_stocks() -> list[dict]:
    """Load stock records from the JSON data file."""
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("/stocks", response_model=list[Stock])
async def get_stocks(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    search: Optional[str] = Query(None, description="Search by ticker or name"),
) -> list[dict]:
    """Return stock data with optional filters."""
    stocks = _load_stocks()

    if sector:
        stocks = [s for s in stocks if s.get("sector", "").lower() == sector.lower()]
    if min_price is not None:
        stocks = [s for s in stocks if s.get("price", 0) >= min_price]
    if max_price is not None:
        stocks = [s for s in stocks if s.get("price", 0) <= max_price]
    if search:
        term = search.lower()
        stocks = [
            s
            for s in stocks
            if term in s.get("ticker", "").lower() or term in s.get("name", "").lower()
        ]

    return stocks
