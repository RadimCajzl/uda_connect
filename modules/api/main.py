import datetime as dt
from typing import List

import fastapi
import fastapi.middleware.cors
import pymongo.collection

import app.config
import app.udaconnect.models
from app.udaconnect.services import ConnectionService, LocationService, PersonService

uda_app = fastapi.FastAPI()

## Add CORS-headers. Required for React-frontend to be able to connect
# to our api.
# see https://fastapi.tiangolo.com/tutorial/cors/?h=%20cors#use-corsmiddleware
# for more details.

uda_app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=[
        "http://localhost:8001",
        "http://localhost:30000",
        "http://localhost:30001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def mongodb_collections() -> app.udaconnect.models.UdaMongoCollections:
    mongo_client: pymongo.MongoClient = pymongo.MongoClient(
        app.config.MONGO_CONNECTION_URI
    )
    mongo_db = mongo_client[app.config.MONGO_DB_NAME]
    return app.udaconnect.models.UdaMongoCollections(
        person=mongo_db["person"], location=mongo_db["location"]
    )


@uda_app.post("/locations", response_model=app.udaconnect.models.Location)
async def create_location(
    request_body: app.udaconnect.models.Location,
    mongo_collections: app.udaconnect.models.UdaMongoCollections = fastapi.Depends(
        mongodb_collections
    ),
) -> app.udaconnect.models.Location:
    return LocationService(mongo_collections=mongo_collections).create(request_body)


@uda_app.post("/persons", response_model=app.udaconnect.models.Person)
async def create_person(
    request_body: app.udaconnect.models.Person,
    mongo_collections: app.udaconnect.models.UdaMongoCollections = fastapi.Depends(
        mongodb_collections
    ),
) -> app.udaconnect.models.Person:
    return PersonService(mongo_collections=mongo_collections).create(request_body)


@uda_app.get("/persons", response_model=List[app.udaconnect.models.Person])
async def get_all_people(
    mongo_collections: app.udaconnect.models.UdaMongoCollections = fastapi.Depends(
        mongodb_collections
    ),
) -> List[app.udaconnect.models.Person]:
    return PersonService(mongo_collections=mongo_collections).retrieve_all()


@uda_app.get("/persons/{person_id}")
async def get_one_person(
    person_id: int,
    mongo_collections: app.udaconnect.models.UdaMongoCollections = fastapi.Depends(
        mongodb_collections
    ),
) -> app.udaconnect.models.Person:
    return PersonService(mongo_collections=mongo_collections).retrieve(
        person_id=person_id
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
    mongo_collections: app.udaconnect.models.UdaMongoCollections = fastapi.Depends(
        mongodb_collections
    ),
) -> List[app.udaconnect.models.Connection]:
    return ConnectionService(mongo_collections=mongo_collections).find_contacts(
        person_id=person_id,
        start_date=dt.datetime.combine(start_date, dt.time(0, 0, 0)),
        end_date=dt.datetime.combine(end_date, dt.time(23, 59, 59)),
        meters=distance,
    )
