"""Pydantic models for the Stock Universe API."""

from __future__ import annotations

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
    sedol: str | None = Field(None, alias="SEDOL")
    figi: str | None = Field(None, alias="FIGI")
    datastream_code: str | None = Field(None, alias="Datastream Code")
    barra_id: str | None = Field(None, alias="Barra ID")
    barra_root_id: str | None = Field(None, alias="Barra Root ID")

    # Fundamentals
    price: float | None = Field(None, alias="Price")
    market_cap: float | None = Field(None, alias="Market_Cap")
    pe_ratio: float | None = Field(None, alias="Pe_Ratio")
    pb_ratio: float | None = Field(None, alias="Pb_Ratio")
    dividend_yield: float | None = Field(None, alias="Dividend_Yield")
    eps: float | None = Field(None, alias="Earnings_Per_Share")
    roe: float | None = Field(None, alias="Return_On_Equity")
    turnover: float | None = Field(None, alias="Turnover_By_Value")
    price_return: float | None = Field(None, alias="Price_Return")
    total_return: float | None = Field(None, alias="Total_Return")
    unadjusted_price: float | None = Field(None, alias="Unadjusted_Price")

    # Returns
    return_1m: float | None = Field(None, alias="Return_1M")
    return_3m: float | None = Field(None, alias="Return_3M")
    return_6m: float | None = Field(None, alias="Return_6M")
    return_1y: float | None = Field(None, alias="Return_1Y")
    return_3y: float | None = Field(None, alias="Return_3Y")
    return_5y: float | None = Field(None, alias="Return_5Y")
    return_10y: float | None = Field(None, alias="Return_10Y")
    return_ytd: float | None = Field(None, alias="Return_YTD")

    # Volatility
    volatility_1m: float | None = Field(None, alias="Volatility_1M")
    volatility_3m: float | None = Field(None, alias="Volatility_3M")
    volatility_6m: float | None = Field(None, alias="Volatility_6M")
    volatility_1y: float | None = Field(None, alias="Volatility_1Y")
    volatility_3y: float | None = Field(None, alias="Volatility_3Y")
    volatility_5y: float | None = Field(None, alias="Volatility_5Y")
    volatility_10y: float | None = Field(None, alias="Volatility_10Y")
    volatility_ytd: float | None = Field(None, alias="Volatility_YTD")

    # Sharpe
    sharpe_1m: float | None = Field(None, alias="Sharpe_1M")
    sharpe_3m: float | None = Field(None, alias="Sharpe_3M")
    sharpe_1y: float | None = Field(None, alias="Sharpe_1Y")
    sharpe_3y: float | None = Field(None, alias="Sharpe_3Y")
    sharpe_5y: float | None = Field(None, alias="Sharpe_5Y")
    sharpe_10y: float | None = Field(None, alias="Sharpe_10Y")

    # Sortino
    sortino_1m: float | None = Field(None, alias="Sortino_1M")
    sortino_3m: float | None = Field(None, alias="Sortino_3M")
    sortino_1y: float | None = Field(None, alias="Sortino_1Y")
    sortino_3y: float | None = Field(None, alias="Sortino_3Y")
    sortino_5y: float | None = Field(None, alias="Sortino_5Y")
    sortino_10y: float | None = Field(None, alias="Sortino_10Y")

    # Max Drawdown
    max_drawdown_1m: float | None = Field(None, alias="Max_Drawdown_1M")
    max_drawdown_3m: float | None = Field(None, alias="Max_Drawdown_3M")
    max_drawdown_1y: float | None = Field(None, alias="Max_Drawdown_1Y")
    max_drawdown_3y: float | None = Field(None, alias="Max_Drawdown_3Y")
    max_drawdown_5y: float | None = Field(None, alias="Max_Drawdown_5Y")
    max_drawdown_10y: float | None = Field(None, alias="Max_Drawdown_10Y")

    # VaR
    var_1m: float | None = Field(None, alias="VaR_1M")
    var_3m: float | None = Field(None, alias="VaR_3M")
    var_1y: float | None = Field(None, alias="VaR_1Y")
    var_3y: float | None = Field(None, alias="VaR_3Y")
    var_5y: float | None = Field(None, alias="VaR_5Y")
    var_10y: float | None = Field(None, alias="VaR_10Y")

    # Skewness / Kurtosis
    skewness_1y: float | None = Field(None, alias="Skewness_1Y")
    kurtosis_1y: float | None = Field(None, alias="Kurtosis_1Y")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Filter models -- used by the NLP-to-filters pipeline
# ---------------------------------------------------------------------------


class NumericRange(BaseModel):
    """Min/max bounds for a numeric filter. Either side may be omitted."""

    min: float | None = Field(default=None, description="Inclusive lower bound")
    max: float | None = Field(default=None, description="Inclusive upper bound")


class UniverseFilters(BaseModel):
    """Structured filters extracted from a user's natural-language query.

    Every field is optional -- only the filters the user explicitly or
    implicitly requested should be populated.
    """

    # -- Categorical --------------------------------------------------------
    countries: list[str] | None = Field(
        default=None,
        description="Country names to include, e.g. ['United States', 'Japan']",
    )
    industries: list[str] | None = Field(
        default=None,
        description=(
            "Industry names, e.g. ['Technology', 'Healthcare']. "
            "Valid values include: Academic & Educational Services, Basic Materials, "
            "Consumer Cyclicals, Consumer Non-Cyclicals, Energy, Financials, "
            "Healthcare, Industrials, Real Estate, Technology, Utilities."
        ),
    )
    sub_industries: list[str] | None = Field(
        default=None,
        description="Sub-industry names, e.g. ['Software & IT Services']",
    )
    currencies: list[str] | None = Field(
        default=None,
        description="ISO currency codes, e.g. ['USD', 'EUR']",
    )
    exchanges: list[str] | None = Field(
        default=None,
        description="Exchange names, e.g. ['NYSE', 'Nasdaq']",
    )

    # -- Text search --------------------------------------------------------
    search: str | None = Field(
        default=None,
        description="Substring to match against ticker or company name",
    )

    # -- Fundamental metrics (NumericRange) ---------------------------------
    price: NumericRange | None = Field(default=None, description="Stock price filter")
    market_cap: NumericRange | None = Field(
        default=None, description="Market capitalisation filter"
    )
    pe_ratio: NumericRange | None = Field(default=None, description="Price-to-earnings ratio")
    pb_ratio: NumericRange | None = Field(default=None, description="Price-to-book ratio")
    dividend_yield: NumericRange | None = Field(default=None, description="Dividend yield (%)")
    earnings_per_share: NumericRange | None = Field(
        default=None, description="Earnings per share"
    )
    return_on_equity: NumericRange | None = Field(
        default=None, description="Return on equity (%)"
    )

    # -- Return metrics -----------------------------------------------------
    return_1m: NumericRange | None = Field(default=None, description="1-month return")
    return_3m: NumericRange | None = Field(default=None, description="3-month return")
    return_6m: NumericRange | None = Field(default=None, description="6-month return")
    return_1y: NumericRange | None = Field(default=None, description="1-year return")
    return_3y: NumericRange | None = Field(default=None, description="3-year return")
    return_5y: NumericRange | None = Field(default=None, description="5-year return")
    return_ytd: NumericRange | None = Field(default=None, description="Year-to-date return")

    # -- Risk metrics -------------------------------------------------------
    volatility_1y: NumericRange | None = Field(default=None, description="1-year volatility")
    sharpe_1y: NumericRange | None = Field(default=None, description="1-year Sharpe ratio")
    sortino_1y: NumericRange | None = Field(default=None, description="1-year Sortino ratio")
    max_drawdown_1y: NumericRange | None = Field(
        default=None, description="1-year max drawdown (negative value)"
    )


# ---------------------------------------------------------------------------
# Chat request / response
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    """A single message in the conversation history."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Incoming chat request with full conversation history."""

    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    """AI agent reply, optionally including extracted filters and an action."""

    reply: str
    filters: UniverseFilters | None = None
    action: str = "none"
