import base.models
from base.base_app import create_base_app
from location_api.location_collector import LocationCollector

uda_app = create_base_app()


@uda_app.post("/locations", response_model=base.models.Location)
async def create_location(
    request_body: base.models.Location,
) -> base.models.Location:
    return LocationCollector().create(request_body)
