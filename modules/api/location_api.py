import fastapi
import fastapi.middleware.cors
import pymongo.collection

import app.config
import app.udaconnect.models
from app.udaconnect.location_service import LocationService
from base_app import create_base_app, location_collection

uda_app = create_base_app()


@uda_app.post("/locations", response_model=app.udaconnect.models.Location)
async def create_location(
    request_body: app.udaconnect.models.Location,
    location_collection: pymongo.collection.Collection = fastapi.Depends(
        location_collection
    ),
) -> app.udaconnect.models.Location:
    return LocationService(location_collection=location_collection).create(request_body)
