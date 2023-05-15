import datetime as dt
from typing import List

import fastapi
import fastapi.middleware.cors
import pymongo.collection

import app.config
import app.udaconnect.models
from app.udaconnect.connection_aggregator import ConnectionAggregator
from base_app import create_base_app, location_collection, person_collection

uda_app = create_base_app()


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
    return ConnectionAggregator(
        person_collection=person_collection, location_collection=location_collection
    ).find_contacts(
        person_id=person_id,
        start_date=dt.datetime.combine(start_date, dt.time(0, 0, 0)),
        end_date=dt.datetime.combine(end_date, dt.time(23, 59, 59)),
        meters=distance,
    )
