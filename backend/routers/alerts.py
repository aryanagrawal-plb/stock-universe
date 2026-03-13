"""Alert / watchlist management API router."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.schemas import Alert, AlertCreate, NumericRange, TriggeredAlert, UniverseFilters

router = APIRouter(tags=["alerts"])

# ---------------------------------------------------------------------------
# In-memory store, seeded with dummy alerts
# ---------------------------------------------------------------------------

_alerts: list[Alert] = [
    Alert(
        id="seed-1",
        name="European High Dividend",
        filters=UniverseFilters(
            countries=[
                "United Kingdom", "France", "Germany", "Switzerland",
                "Netherlands", "Spain", "Italy", "Sweden",
            ],
            dividend_yield=NumericRange(min=4.0),
        ),
        created_at="2026-02-10T09:30:00Z",
        status="active",
    ),
    Alert(
        id="seed-2",
        name="US Tech Growth",
        filters=UniverseFilters(
            countries=["United States"],
            industries=["Technology"],
            return_1y=NumericRange(min=0.15),
        ),
        created_at="2026-02-18T14:15:00Z",
        status="active",
    ),
    Alert(
        id="seed-3",
        name="Japanese Value Stocks",
        filters=UniverseFilters(
            countries=["Japan"],
            pe_ratio=NumericRange(max=12.0),
            pb_ratio=NumericRange(max=1.5),
        ),
        created_at="2026-03-01T11:00:00Z",
        status="paused",
    ),
    Alert(
        id="seed-4",
        name="Emerging Market Energy",
        filters=UniverseFilters(
            countries=["Brazil", "India", "China"],
            industries=["Energy"],
        ),
        created_at="2026-03-05T16:45:00Z",
        status="active",
    ),
    Alert(
        id="seed-5",
        name="Low Volatility Blue Chips",
        filters=UniverseFilters(
            market_cap=NumericRange(min=50000.0),
            volatility_1y=NumericRange(max=0.2),
        ),
        created_at="2026-03-10T08:20:00Z",
        status="active",
    ),
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


_TRIGGERED_OFFSETS = [
    (timedelta(minutes=5), 12),
    (timedelta(minutes=47), 38),
    (timedelta(hours=3), 7),
]


@router.get("/alerts/triggered", response_model=list[TriggeredAlert])
async def list_triggered_alerts() -> list[TriggeredAlert]:
    """Return active alerts whose conditions are spoofed as met."""
    now = datetime.now(timezone.utc)
    active = [a for a in _alerts if a.status == "active"]
    triggered: list[TriggeredAlert] = []
    for alert, (offset, count) in zip(active[:3], _TRIGGERED_OFFSETS):
        triggered.append(
            TriggeredAlert(
                alert=alert,
                triggered_at=(now - offset).isoformat(),
                match_count=count,
            )
        )
    return triggered


@router.get("/alerts", response_model=list[Alert])
async def list_alerts() -> list[Alert]:
    """Return all alerts, newest first."""
    return sorted(_alerts, key=lambda a: a.created_at, reverse=True)


@router.post("/alerts", response_model=Alert, status_code=201)
async def create_alert(body: AlertCreate) -> Alert:
    """Create a new alert from a name and filter set."""
    alert = Alert(
        id=str(uuid.uuid4()),
        name=body.name,
        filters=body.filters,
        created_at=datetime.now(timezone.utc).isoformat(),
        status="active",
    )
    _alerts.append(alert)
    return alert


@router.delete("/alerts/{alert_id}", status_code=204)
async def delete_alert(alert_id: str) -> None:
    """Delete an alert by ID."""
    global _alerts  # noqa: PLW0603
    before = len(_alerts)
    _alerts = [a for a in _alerts if a.id != alert_id]
    if len(_alerts) == before:
        raise HTTPException(status_code=404, detail="Alert not found")


class _StatusPatch(BaseModel):
    status: str


@router.patch("/alerts/{alert_id}", response_model=Alert)
async def patch_alert(alert_id: str, body: _StatusPatch) -> Alert:
    """Toggle an alert's status (active / paused)."""
    if body.status not in ("active", "paused"):
        raise HTTPException(status_code=422, detail="status must be 'active' or 'paused'")
    for alert in _alerts:
        if alert.id == alert_id:
            alert.status = body.status
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")
