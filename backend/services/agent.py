"""AI agent service – converts natural-language queries into structured stock filters.

Uses the DeepSeek API (OpenAI-compatible) with JSON-object mode to reliably
extract a ``UniverseFilters`` object from free-form text, supporting add,
remove, and clear actions with full conversation history.
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

MAX_HISTORY_MESSAGES = 20


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
# System prompt – tells the LLM what filters are available and how to respond
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a stock-universe filter assistant.  You read the user's
natural-language request and produce a JSON object with exactly three keys:

  {
    "reply":   "<short conversational message to the user>",
    "action":  "<one of: set, add, remove, clear, none>",
    "filters": { ... UniverseFilters ... }
  }

### Action rules

- **set**    – the user wants to REPLACE the current filters with a new set.
               Use this when the user describes the complete desired state
               (e.g. "show only India energy", "switch to Japan tech",
               "I want US healthcare stocks").  The previous filters will be
               discarded and replaced by the ones you provide.
- **add**    – the user wants to ADD filters ON TOP of what is already active.
               Use this when they say "also", "additionally", "include",
               or just ask for something without implying the old filters
               should be removed.
- **remove** – the user wants to REMOVE specific active filters.  Populate
               "filters" with the fields to remove (e.g. to remove the
               country filter, set "countries": ["United States"]).
- **clear**  – the user wants to CLEAR ALL filters.  Set "filters" to {}.
- **none**   – the user is asking a general question, chatting, or the
               request doesn't map to any filter change.  Set "filters" to {}.

### How to choose between "set" and "add"

- "Show me India energy stocks" after a previous filter → **set** (replaces)
- "Show only X" / "Switch to X" / "I want X" → **set** (replaces)
- "Also show Japan" / "Add technology" → **add** (merges)
- If unsure whether the user wants to replace or add, default to **set**.

### Reply guidelines

- Keep replies short (1-3 sentences).
- When action is "set", say what the new filters will be.
- When action is "add", say what you're adding to the existing filters.
- When action is "remove", summarise what you're suggesting to remove.
- When action is "clear", confirm that all filters will be cleared.
- When action is "none", answer the user's question helpfully.

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

### Filter rules
- Only set filter fields the user explicitly or implicitly requested.
- Leave every other filter field out of the JSON (do NOT set them to null).
- "show me tech stocks" → action: "set", industries: ["Technology"]
- "show India and China energy" → action: "set", countries: ["India","China"], industries: ["Energy"]
- "show only India energy" (after above) → action: "set", countries: ["India"], industries: ["Energy"]
- "also add Japan" → action: "add", countries: ["Japan"]
- "cheap stocks" → action: "set", price: {"max": 20}
- "high dividend" → action: "set", dividend_yield: {"min": 3}
- "large cap" → action: "set", market_cap: {"min": 10000}
- "remove country filter" → action: "remove", countries: [<whatever was set>]
- "clear all filters" → action: "clear"
- "hello" / general question → action: "none"
"""


# ---------------------------------------------------------------------------
# Public entry point (used by the /chat router)
# ---------------------------------------------------------------------------


async def process_message(
    messages: list[dict[str, str]],
) -> tuple[str, str, UniverseFilters | None]:
    """Process a conversation and return reply, action, and extracted filters.

    Args:
        messages: Full conversation history as list of {"role": ..., "content": ...}.

    Returns:
        A tuple of (reply text, action string, parsed filters or None).
    """
    try:
        return await _call_llm(messages)
    except Exception:
        logger.exception("Failed to process message through LLM")
        return (
            "Sorry, I couldn't interpret your request. Please try rephrasing.",
            "none",
            None,
        )


async def _call_llm(
    messages: list[dict[str, str]],
) -> tuple[str, str, UniverseFilters | None]:
    """Call DeepSeek with conversation history and parse the structured response."""
    client = _get_client()

    trimmed = messages[-MAX_HISTORY_MESSAGES:]
    api_messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{"role": m["role"], "content": m["content"]} for m in trimmed],
    ]

    response = await client.chat.completions.create(
        model="deepseek-chat",
        temperature=0,
        messages=api_messages,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    logger.debug("DeepSeek raw response: %s", raw)

    try:
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Failed to parse DeepSeek response as JSON: %s", raw)
        return ("I had trouble understanding that. Could you rephrase?", "none", None)

    reply = data.get("reply", "")
    action = data.get("action", "none")
    if action not in ("set", "add", "remove", "clear", "none"):
        action = "none"

    raw_filters = data.get("filters", {})
    if not isinstance(raw_filters, dict):
        raw_filters = {}

    cleaned = _strip_nulls(raw_filters)
    filters: UniverseFilters | None = None

    if action in ("set", "add", "remove") and cleaned:
        try:
            filters = UniverseFilters.model_validate(cleaned)
        except ValidationError as exc:
            logger.warning("Filter validation failed: %s", exc)
            filters = None

    if not reply:
        reply = _generate_fallback_reply(action, filters)

    return reply, action, filters


def _generate_fallback_reply(
    action: str, filters: UniverseFilters | None
) -> str:
    """Create a reply when the LLM didn't provide one."""
    if action == "clear":
        return "I'll clear all active filters."
    if action == "none":
        return "I'm not sure what you'd like me to do. Try asking me to filter stocks."
    if filters is None:
        return "I couldn't detect any specific filters in your message."
    summary = summarise_filters(filters)
    verb = "add" if action == "add" else "remove"
    return f"I'd like to {verb} these filters:\n{summary}"


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
# Helpers
# ---------------------------------------------------------------------------


def _strip_nulls(obj: Any) -> Any:
    """Recursively remove keys whose value is ``None`` from dicts."""
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(i) for i in obj]
    return obj
