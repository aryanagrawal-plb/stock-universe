"""AI agent service – converts natural-language queries into structured stock filters.

Uses the DeepSeek API (OpenAI-compatible) with JSON-object mode to reliably
extract a ``UniverseFilters`` object from free-form text.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import ValidationError

from models.schemas import NumericRange, UniverseFilters

load_dotenv()

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Lazily initialise the DeepSeek async client (OpenAI-compatible)."""
    global _client  # noqa: PLW0603
    if _client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is not set. "
                "Add it to your .env file or export it as an environment variable."
            )
        _client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return _client


# ---------------------------------------------------------------------------
# System prompt – tells the LLM what filters are available and how to use them
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a stock-universe filter assistant.  Your ONLY job is to read the
user's natural-language request and produce a JSON object that conforms to
the UniverseFilters schema.  Never add commentary – return ONLY valid JSON.

### Available categorical values

**Countries** (use exact spelling):
Australia, Austria, Belgium, Bermuda, Brazil, Canada, Chile, China,
Colombia, Czech Republic, Denmark, Egypt, Finland, France, Germany, Greece,
Hong Kong, Hungary, India, Indonesia, Ireland, Israel, Italy, Japan, Kuwait,
Luxembourg, Malaysia, Mexico, Netherlands, New Zealand, Norway, Peru,
Philippines, Poland, Portugal, Qatar, Russian Federation, Saudi Arabia,
Singapore, South Africa, South Korea, Spain, Sweden, Switzerland, Taiwan,
Thailand, Turkey, United Arab Emirates, United Kingdom, United States

**Industries**:
Academic & Educational Services, Basic Materials, Consumer Cyclicals,
Consumer Non-Cyclicals, Energy, Financials, Healthcare, Industrials,
Real Estate, Technology, Utilities

**Sub-Industries** (partial list):
Applied Resources, Automobiles & Auto Parts, Banking & Investment Services,
Chemicals, Cyclical Consumer Products, Cyclical Consumer Services,
Energy - Fossil Fuels, Food & Beverages, Food & Drug Retailing,
Healthcare Services & Equipment, Holding Companies,
Industrial & Commercial Services, Industrial Goods, Insurance,
Mineral Resources, Personal & Household Products & Services,
Pharmaceuticals & Medical Research, Real Estate, Renewable Energy,
Retailers, Software & IT Services, Technology Equipment,
Telecommunications Services, Transportation, Uranium, Utilities

**Currencies** (ISO codes):
AED, AUD, BRL, CAD, CHF, CLP, CNH, CNY, COP, CZK, DKK, EGP, EUR, GBP,
HKD, HUF, IDR, ILS, INR, JPY, KRW, KWD, MXN, MYR, NOK, NZD, PHP, PLN,
QAR, RUB, SAR, SEK, SGD, THB, TRY, TWD, USD, ZAR

**Exchanges**:
Australian SE, B3 Brasil Bolsa, BME Exchange, Boerse Frankfurt,
Borsa Italiana, Bursa Malaysia, Euronext Amsterdam, Euronext Paris,
Hong Kong Exchange, Indonesia SE, Johannesburg SE, Korea Exchange,
London SE, Moscow Exchange, NASDAQ, Nasdaq, NYSE, NYSE American,
Oslo Bors, Santiago SE, Saudi SE, Shanghai SE, Shenzhen SE,
Singapore Exchange, Six Swiss Exchange, Taipei SE, Taiwan SE,
Tel Aviv SE, Thailand SE, Tokyo SE, Toronto SE, Warsaw SE, XETRA

### Numeric range filters

For any numeric filter, set ``min`` and/or ``max``.  Omit the key entirely
if the user did not mention it.

| Filter key           | What it means                       |
|----------------------|-------------------------------------|
| price                | Stock price                         |
| market_cap           | Market capitalisation               |
| pe_ratio             | Price-to-Earnings ratio             |
| pb_ratio             | Price-to-Book ratio                 |
| dividend_yield       | Dividend yield (percentage points)  |
| earnings_per_share   | EPS                                 |
| return_on_equity     | ROE (percentage points)             |
| return_1m            | 1-month return                      |
| return_3m            | 3-month return                      |
| return_6m            | 6-month return                      |
| return_1y            | 1-year return                       |
| return_3y            | 3-year return                       |
| return_5y            | 5-year return                       |
| return_ytd           | Year-to-date return                 |
| volatility_1y        | 1-year annualised volatility        |
| sharpe_1y            | 1-year Sharpe ratio                 |
| sortino_1y           | 1-year Sortino ratio                |
| max_drawdown_1y      | 1-year max drawdown (negative)      |

### Text search

Set ``search`` to a substring if the user wants to find stocks by ticker
symbol or company name (e.g. "Apple", "AAPL").

### Rules
- Only set fields the user explicitly or implicitly requested.
- Leave every other field out of the JSON (do NOT set them to null).
- "tech stocks" → industries: ["Technology"]
- "cheap stocks" → price: {"max": 20}
- "high dividend" → dividend_yield: {"min": 3}
- "large cap" → market_cap: {"min": 10000}  (units are millions)
- "small cap" → market_cap: {"max": 2000}
- If the user's request doesn't map to any filter, return an empty JSON object {}.
"""


# ---------------------------------------------------------------------------
# Core parse function
# ---------------------------------------------------------------------------


async def parse_filters_from_nl(message: str) -> UniverseFilters:
    """Parse a natural-language message into a ``UniverseFilters`` object.

    Args:
        message: Free-form user text, e.g. "Show me US tech stocks under $50".

    Returns:
        A populated ``UniverseFilters`` instance with only the relevant
        filters set.

    Raises:
        RuntimeError: If the DeepSeek API key is missing or the API call fails.
    """
    client = _get_client()

    response = await client.chat.completions.create(
        model="deepseek-chat",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    logger.debug("DeepSeek raw response: %s", raw)

    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse DeepSeek response as JSON: %s", raw)
        return UniverseFilters()

    cleaned = _strip_nulls(data)

    try:
        return UniverseFilters.model_validate(cleaned)
    except ValidationError as exc:
        logger.warning("Filter validation failed: %s", exc)
        return UniverseFilters()


# ---------------------------------------------------------------------------
# Human-readable summary
# ---------------------------------------------------------------------------

_LABEL_MAP: dict[str, str] = {
    "countries": "Country",
    "industries": "Industry",
    "sub_industries": "Sub-Industry",
    "currencies": "Currency",
    "exchanges": "Exchange",
    "search": "Search",
    "price": "Price",
    "market_cap": "Market Cap",
    "pe_ratio": "P/E Ratio",
    "pb_ratio": "P/B Ratio",
    "dividend_yield": "Dividend Yield",
    "earnings_per_share": "EPS",
    "return_on_equity": "ROE",
    "return_1m": "1M Return",
    "return_3m": "3M Return",
    "return_6m": "6M Return",
    "return_1y": "1Y Return",
    "return_3y": "3Y Return",
    "return_5y": "5Y Return",
    "return_ytd": "YTD Return",
    "volatility_1y": "1Y Volatility",
    "sharpe_1y": "1Y Sharpe",
    "sortino_1y": "1Y Sortino",
    "max_drawdown_1y": "1Y Max Drawdown",
}


def summarise_filters(filters: UniverseFilters) -> str:
    """Build a human-readable summary string from populated filter fields.

    Args:
        filters: The parsed filter object.

    Returns:
        A short description such as
        ``"Country = United States, Industry = Technology, P/E Ratio <= 30"``.
        Returns ``"No filters detected."`` when every field is ``None``.
    """
    parts: list[str] = []
    data = filters.model_dump(exclude_none=True)

    if not data:
        return "No filters detected."

    for key, value in data.items():
        label = _LABEL_MAP.get(key, key)

        if isinstance(value, list):
            parts.append(f"{label} = {', '.join(value)}")
        elif isinstance(value, str):
            parts.append(f"{label} contains '{value}'")
        elif isinstance(value, dict):
            rng = NumericRange(**value)
            if rng.min is not None and rng.max is not None:
                parts.append(f"{rng.min} <= {label} <= {rng.max}")
            elif rng.min is not None:
                parts.append(f"{label} >= {rng.min}")
            elif rng.max is not None:
                parts.append(f"{label} <= {rng.max}")

    return ", ".join(parts) if parts else "No filters detected."


# ---------------------------------------------------------------------------
# Public entry point (used by the /chat router)
# ---------------------------------------------------------------------------


async def process_message(message: str) -> tuple[str, UniverseFilters | None]:
    """Process a user message and return a summary + extracted filters.

    Args:
        message: The user's chat message.

    Returns:
        A tuple of (human-readable reply, parsed filters or None on error).
    """
    try:
        filters = await parse_filters_from_nl(message)
    except Exception:
        logger.exception("Failed to parse filters from message")
        return (
            "Sorry, I couldn't interpret your request. Please try rephrasing.",
            None,
        )

    summary = summarise_filters(filters)
    has_filters = bool(filters.model_dump(exclude_none=True))

    if has_filters:
        reply = (
            f"I understood the following filters from your request:\n\n"
            f"{summary}\n\n"
            f"Would you like me to apply these filters?"
        )
    else:
        reply = (
            "I couldn't detect any specific filters in your message. "
            "Try something like: \"Show me US tech stocks with PE under 25\"."
        )

    return reply, filters if has_filters else None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_nulls(obj: Any) -> Any:
    """Recursively remove keys whose value is ``None`` from dicts."""
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(i) for i in obj]
    return obj


def _build_json_schema() -> dict[str, Any]:
    """Build the JSON Schema describing ``UniverseFilters``.

    This schema is no longer sent to the API (DeepSeek uses prompt-based
    JSON-object mode), but is retained for documentation and potential
    future use with providers that support strict schema enforcement.
    """
    numeric_range = {
        "type": "object",
        "properties": {
            "min": {"anyOf": [{"type": "number"}, {"type": "null"}]},
            "max": {"anyOf": [{"type": "number"}, {"type": "null"}]},
        },
        "required": ["min", "max"],
        "additionalProperties": False,
    }

    nullable_range = {"anyOf": [numeric_range, {"type": "null"}]}
    nullable_str_array = {
        "anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]
    }
    nullable_str = {"anyOf": [{"type": "string"}, {"type": "null"}]}

    properties: dict[str, Any] = {}
    required: list[str] = []

    categorical_keys = ["countries", "industries", "sub_industries", "currencies", "exchanges"]
    for key in categorical_keys:
        properties[key] = nullable_str_array
        required.append(key)

    properties["search"] = nullable_str
    required.append("search")

    numeric_keys = [
        "price",
        "market_cap",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield",
        "earnings_per_share",
        "return_on_equity",
        "return_1m",
        "return_3m",
        "return_6m",
        "return_1y",
        "return_3y",
        "return_5y",
        "return_ytd",
        "volatility_1y",
        "sharpe_1y",
        "sortino_1y",
        "max_drawdown_1y",
    ]
    for key in numeric_keys:
        properties[key] = nullable_range
        required.append(key)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }
