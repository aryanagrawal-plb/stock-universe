"""Pydantic models for the Stock Universe API."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def _none_to_empty(v: object) -> object:
    """Coerce None to empty string for optional text fields."""
    return "" if v is None else v


StrOrEmpty = Annotated[str, BeforeValidator(_none_to_empty)]


class Stock(BaseModel):
    """A single stock record from the universe master dataset."""

    code: str = Field(alias="Code")
    name: str = Field(alias="Name")
    ticker: str = Field(alias="Ticker")
    currency: StrOrEmpty = Field(default="", alias="Currency")
    country: StrOrEmpty = Field(default="", alias="Country")
    industry: StrOrEmpty = Field(default="", alias="Industry")
    sub_industry: StrOrEmpty = Field(default="", alias="Sub-Industry")
    exchange: StrOrEmpty = Field(default="", alias="Exchange")

    # Identifiers
    ric: str | None = Field(None, alias="RIC")
    isin: str | None = Field(None, alias="ISIN")

    # Fundamentals
    price: float | None = Field(None, alias="Price")
    market_cap: float | None = Field(None, alias="Market_Cap")
    pe_ratio: float | None = Field(None, alias="Pe_Ratio")
    pb_ratio: float | None = Field(None, alias="Pb_Ratio")
    dividend_yield: float | None = Field(None, alias="Dividend_Yield")
    eps: float | None = Field(None, alias="Earnings_Per_Share")
    roe: float | None = Field(None, alias="Return_On_Equity")
    turnover: float | None = Field(None, alias="Turnover_By_Value")

    # Returns
    return_1m: float | None = Field(None, alias="Return_1M")
    return_3m: float | None = Field(None, alias="Return_3M")
    return_6m: float | None = Field(None, alias="Return_6M")
    return_1y: float | None = Field(None, alias="Return_1Y")
    return_ytd: float | None = Field(None, alias="Return_YTD")

    # Risk
    volatility_1y: float | None = Field(None, alias="Volatility_1Y")
    sharpe_1y: float | None = Field(None, alias="Sharpe_1Y")
    max_drawdown_1y: float | None = Field(None, alias="Max_Drawdown_1Y")

    model_config = {"populate_by_name": True}


class ChatRequest(BaseModel):
    """Incoming chat message from the user."""

    message: str


class ChatResponse(BaseModel):
    """AI agent reply."""

    reply: str
