"""Tests for the NLP-to-filters agent pipeline."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.schemas import NumericRange, UniverseFilters
from services.agent import (
    _build_json_schema,
    _strip_nulls,
    parse_filters_from_nl,
    summarise_filters,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _mock_llm_response(content: dict) -> MagicMock:
    """Build a mock that mimics ``chat.completions.create()`` output (OpenAI-compatible)."""
    message = MagicMock()
    message.content = json.dumps(content)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestUniverseFilters:
    """Tests for the UniverseFilters Pydantic model."""

    def test_empty_filters(self) -> None:
        """Should construct with all fields defaulting to None."""
        filters = UniverseFilters()
        assert filters.model_dump(exclude_none=True) == {}

    def test_categorical_filters(self) -> None:
        """Should accept categorical list fields."""
        filters = UniverseFilters(
            countries=["United States", "Japan"],
            industries=["Technology"],
        )
        data = filters.model_dump(exclude_none=True)
        assert data["countries"] == ["United States", "Japan"]
        assert data["industries"] == ["Technology"]
        assert "currencies" not in data

    def test_numeric_range_filters(self) -> None:
        """Should accept NumericRange objects for numeric fields."""
        filters = UniverseFilters(
            price=NumericRange(min=10, max=50),
            pe_ratio=NumericRange(max=30),
        )
        data = filters.model_dump(exclude_none=True)
        assert data["price"] == {"min": 10.0, "max": 50.0}
        assert data["pe_ratio"] == {"max": 30.0}

    def test_search_field(self) -> None:
        """Should accept a text search string."""
        filters = UniverseFilters(search="AAPL")
        data = filters.model_dump(exclude_none=True)
        assert data["search"] == "AAPL"

    def test_mixed_filters(self) -> None:
        """Should handle a combination of categorical, numeric, and search."""
        filters = UniverseFilters(
            countries=["United States"],
            industries=["Healthcare"],
            dividend_yield=NumericRange(min=2.0),
            return_1y=NumericRange(min=0.1),
            search="pharma",
        )
        data = filters.model_dump(exclude_none=True)
        assert len(data) == 5


# ---------------------------------------------------------------------------
# Summarise tests
# ---------------------------------------------------------------------------


class TestSummariseFilters:
    """Tests for the summarise_filters helper."""

    def test_empty_filters_summary(self) -> None:
        """Should return a 'no filters' message for empty filters."""
        assert summarise_filters(UniverseFilters()) == "No filters detected."

    def test_categorical_summary(self) -> None:
        """Should list categorical values."""
        filters = UniverseFilters(
            countries=["United States"],
            industries=["Technology", "Healthcare"],
        )
        summary = summarise_filters(filters)
        assert "Country = United States" in summary
        assert "Industry = Technology, Healthcare" in summary

    def test_range_summary(self) -> None:
        """Should format numeric ranges with >= / <= operators."""
        filters = UniverseFilters(
            pe_ratio=NumericRange(max=30),
            dividend_yield=NumericRange(min=2.0),
            price=NumericRange(min=10, max=100),
        )
        summary = summarise_filters(filters)
        assert "P/E Ratio <= 30" in summary
        assert "Dividend Yield >= 2.0" in summary
        assert "10.0 <= Price <= 100.0" in summary

    def test_search_summary(self) -> None:
        """Should show 'contains' for search text."""
        filters = UniverseFilters(search="AAPL")
        summary = summarise_filters(filters)
        assert "Search contains 'AAPL'" in summary


# ---------------------------------------------------------------------------
# parse_filters_from_nl tests (mocked DeepSeek)
# ---------------------------------------------------------------------------


class TestParseFiltersFromNl:
    """Tests for the main parse_filters_from_nl function with mocked DeepSeek."""

    @pytest.mark.asyncio
    async def test_us_tech_query(self) -> None:
        """Should extract country and industry from a tech-stocks query."""
        mock_response_data = {
            "countries": ["United States"],
            "industries": ["Technology"],
            "sub_industries": None,
            "currencies": None,
            "exchanges": None,
            "search": None,
            "price": None,
            "market_cap": None,
            "pe_ratio": {"min": None, "max": 30.0},
            "pb_ratio": None,
            "dividend_yield": {"min": 2.0, "max": None},
            "earnings_per_share": None,
            "return_on_equity": None,
            "return_1m": None,
            "return_3m": None,
            "return_6m": None,
            "return_1y": None,
            "return_3y": None,
            "return_5y": None,
            "return_ytd": None,
            "volatility_1y": None,
            "sharpe_1y": None,
            "sortino_1y": None,
            "max_drawdown_1y": None,
        }
        mock_resp = _mock_llm_response(mock_response_data)

        with patch("services.agent._get_client") as mock_get_client:
            client = AsyncMock()
            client.chat.completions.create = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = client

            filters = await parse_filters_from_nl(
                "Show me US tech stocks with PE under 30 and dividend yield above 2%"
            )

        assert filters.countries == ["United States"]
        assert filters.industries == ["Technology"]
        assert filters.pe_ratio is not None
        assert filters.pe_ratio.max == 30.0
        assert filters.dividend_yield is not None
        assert filters.dividend_yield.min == 2.0

    @pytest.mark.asyncio
    async def test_empty_message(self) -> None:
        """Should return empty filters for a no-filter message."""
        mock_response_data = {
            "countries": None,
            "industries": None,
            "sub_industries": None,
            "currencies": None,
            "exchanges": None,
            "search": None,
            "price": None,
            "market_cap": None,
            "pe_ratio": None,
            "pb_ratio": None,
            "dividend_yield": None,
            "earnings_per_share": None,
            "return_on_equity": None,
            "return_1m": None,
            "return_3m": None,
            "return_6m": None,
            "return_1y": None,
            "return_3y": None,
            "return_5y": None,
            "return_ytd": None,
            "volatility_1y": None,
            "sharpe_1y": None,
            "sortino_1y": None,
            "max_drawdown_1y": None,
        }
        mock_resp = _mock_llm_response(mock_response_data)

        with patch("services.agent._get_client") as mock_get_client:
            client = AsyncMock()
            client.chat.completions.create = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = client

            filters = await parse_filters_from_nl("Hello, how are you?")

        assert filters.model_dump(exclude_none=True) == {}

    @pytest.mark.asyncio
    async def test_search_query(self) -> None:
        """Should extract a search term from a ticker query."""
        mock_response_data = {
            "countries": None,
            "industries": None,
            "sub_industries": None,
            "currencies": None,
            "exchanges": None,
            "search": "AAPL",
            "price": None,
            "market_cap": None,
            "pe_ratio": None,
            "pb_ratio": None,
            "dividend_yield": None,
            "earnings_per_share": None,
            "return_on_equity": None,
            "return_1m": None,
            "return_3m": None,
            "return_6m": None,
            "return_1y": None,
            "return_3y": None,
            "return_5y": None,
            "return_ytd": None,
            "volatility_1y": None,
            "sharpe_1y": None,
            "sortino_1y": None,
            "max_drawdown_1y": None,
        }
        mock_resp = _mock_llm_response(mock_response_data)

        with patch("services.agent._get_client") as mock_get_client:
            client = AsyncMock()
            client.chat.completions.create = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = client

            filters = await parse_filters_from_nl("AAPL")

        assert filters.search == "AAPL"

    @pytest.mark.asyncio
    async def test_invalid_json_response(self) -> None:
        """Should return empty filters when DeepSeek returns invalid JSON."""
        message = MagicMock()
        message.content = "not valid json {"
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]

        with patch("services.agent._get_client") as mock_get_client:
            client = AsyncMock()
            client.chat.completions.create = AsyncMock(return_value=response)
            mock_get_client.return_value = client

            filters = await parse_filters_from_nl("anything")

        assert filters.model_dump(exclude_none=True) == {}


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------


class TestHelpers:
    """Tests for internal helper functions."""

    def test_strip_nulls_removes_none_values(self) -> None:
        """Should recursively remove None values from dicts."""
        data = {"a": 1, "b": None, "c": {"d": None, "e": 2}}
        assert _strip_nulls(data) == {"a": 1, "c": {"e": 2}}

    def test_strip_nulls_preserves_lists(self) -> None:
        """Should process lists without removing non-None elements."""
        data = {"a": [1, 2, 3], "b": None}
        assert _strip_nulls(data) == {"a": [1, 2, 3]}

    def test_build_json_schema_structure(self) -> None:
        """Should produce a valid JSON Schema with required keys."""
        schema = _build_json_schema()
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "countries" in schema["properties"]
        assert "price" in schema["properties"]
        assert "search" in schema["properties"]
        assert len(schema["required"]) == len(schema["properties"])
