import asyncio
import datetime as dt
from typing import Dict, List, Literal

import fastapi
import fastapi.middleware.cors
import pymongo.collection

import app.config
import app.udaconnect.models
from app.udaconnect.connection_aggregator import ConnectionAggregator
from base_app import create_base_app, location_collection, person_collection

uda_app = create_base_app()


# Auxiliary variables to count for number of connection in last X sec.
CONNECTION_COUNTER_RESET_INTERVAL = dt.timedelta(seconds=5)
_connection_counters: Dict[
    Literal["current", "previous"], app.udaconnect.models.ConnectionCountInterval | None
] = {
    "current": app.udaconnect.models.ConnectionCountInterval(
        count=0, start=dt.datetime.now(), duration=CONNECTION_COUNTER_RESET_INTERVAL
    ),
    "previous": None,
}

_connection_counter_lock = asyncio.Lock()


def _swap_connection_intervals_if_needed() -> None:
    global _connection_counters

    if _connection_counters["current"] is None:
        raise ValueError("Connection counter 'current' must not be None.")
    if (
        _connection_counters["current"].start
        < dt.datetime.now() - _connection_counters["current"].duration
    ):
        _connection_counters["previous"] = _connection_counters["current"]
        _connection_counters["current"] = app.udaconnect.models.ConnectionCountInterval(
            count=0, start=dt.datetime.now(), duration=CONNECTION_COUNTER_RESET_INTERVAL
        )


@uda_app.get(
    "/persons/{person_id}/connection",
    response_model=List[app.udaconnect.models.Connection],
)
async def find_contacts_for_person(
    person_id: int,
    start_date: dt.date,
    end_date: dt.date,
    distance: int = 5,
    location_collection: pymongo.collection.Collection = fastapi.Depends(
        location_collection
    ),
    person_collection: pymongo.collection.Collection = fastapi.Depends(
        person_collection
    ),
) -> List[app.udaconnect.models.Connection]:
    global _connection_counters
    if _connection_counters["current"] is None:
        raise ValueError("Connection counter 'current' must not be None.")
    async with _connection_counter_lock:
        _swap_connection_intervals_if_needed()
        _connection_counters["current"].count += 1

    return ConnectionAggregator(
        person_collection=person_collection, location_collection=location_collection
    ).find_contacts(
        person_id=person_id,
        start_date=dt.datetime.combine(start_date, dt.time(0, 0, 0)),
        end_date=dt.datetime.combine(end_date, dt.time(23, 59, 59)),
        meters=distance,
    )


@uda_app.get("/metrics", response_model=app.udaconnect.models.ApiMetrics)
async def metrics() -> app.udaconnect.models.ApiMetrics:
    """Returns statistics with recent connections."""
    global _connection_counters
    return app.udaconnect.models.ApiMetrics(
        status="healthy", connection_count_intervals=_connection_counters
    )
