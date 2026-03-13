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
        """Should return all stocks when no filters are applied."""
        response = client.get("/api/stocks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10

    def test_filter_by_sector(self, client: TestClient) -> None:
        """Should return only stocks matching the given sector."""
        response = client.get("/api/stocks", params={"sector": "Technology"})
        assert response.status_code == 200
        data = response.json()
        assert all(s["sector"] == "Technology" for s in data)
        assert len(data) == 4

    def test_filter_by_price_range(self, client: TestClient) -> None:
        """Should return stocks within the given price range."""
        response = client.get("/api/stocks", params={"min_price": 150, "max_price": 200})
        assert response.status_code == 200
        data = response.json()
        assert all(150 <= s["price"] <= 200 for s in data)

    def test_search_by_ticker(self, client: TestClient) -> None:
        """Should return stocks matching the search term in ticker or name."""
        response = client.get("/api/stocks", params={"search": "aapl"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ticker"] == "AAPL"

    def test_health_check(self, client: TestClient) -> None:
        """Should return healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
