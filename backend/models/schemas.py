"""Pydantic models for the Stock Universe API."""

from pydantic import BaseModel


class Stock(BaseModel):
    """A single stock record."""

    ticker: str
    name: str
    sector: str
    price: float
    market_cap: float
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    volume: int = 0


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    message: str


class ChatResponse(BaseModel):
    """AI agent reply."""

    reply: str
