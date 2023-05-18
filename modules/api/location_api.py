import app.config
import app.udaconnect.models
from app.udaconnect.location_collector import LocationCollector
from base_app import create_base_app

uda_app = create_base_app()


@uda_app.post("/locations", response_model=app.udaconnect.models.Location)
async def create_location(
    request_body: app.udaconnect.models.Location,
) -> app.udaconnect.models.Location:
    return LocationCollector().create(request_body)
