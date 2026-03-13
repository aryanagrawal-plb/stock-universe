"""Tests for the stocks API endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from main import app

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestStocksEndpoint:
    """Tests for GET /api/stocks."""

    def test_get_all_stocks(self, client: TestClient) -> None:
        """Should return all stocks from the universe master dataset."""
        response = client.get("/api/stocks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_stock_has_expected_fields(self, client: TestClient) -> None:
        """Should return stock records with the expected schema fields."""
        response = client.get("/api/stocks")
        assert response.status_code == 200
        data = response.json()
        first = data[0]
        assert "code" in first
        assert "name" in first
        assert "ticker" in first
        assert "country" in first
        assert "industry" in first

    def test_stock_has_fundamental_fields(self, client: TestClient) -> None:
        """Should include fundamental metrics in stock records."""
        response = client.get("/api/stocks")
        assert response.status_code == 200
        first = response.json()[0]
        for field in ("price", "market_cap", "pe_ratio", "dividend_yield"):
            assert field in first

    def test_health_check(self, client: TestClient) -> None:
        """Should return healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
