from typing import List

import fastapi
import fastapi.middleware.cors
import pymongo.collection

import app.config
import app.udaconnect.models
from app.udaconnect.person_service import PersonService
from base_app import create_base_app, person_collection

uda_app = create_base_app()

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


@uda_app.post("/persons", response_model=app.udaconnect.models.Person)
async def create_person(
    request_body: app.udaconnect.models.Person,
    person_collection: pymongo.collection.Collection = fastapi.Depends(
        person_collection
    ),
) -> app.udaconnect.models.Person:
    return PersonService(person_collection=person_collection).create(request_body)


@uda_app.get("/persons", response_model=List[app.udaconnect.models.Person])
async def get_all_people(
    person_collection: pymongo.collection.Collection = fastapi.Depends(
        person_collection
    ),
) -> List[app.udaconnect.models.Person]:
    return PersonService(person_collection=person_collection).retrieve_all()


@uda_app.get("/persons/{person_id}")
async def get_one_person(
    person_id: int,
    person_collection: pymongo.collection.Collection = fastapi.Depends(
        person_collection
    ),
) -> app.udaconnect.models.Person:
    return PersonService(person_collection=person_collection).retrieve(
        person_id=person_id
    )
