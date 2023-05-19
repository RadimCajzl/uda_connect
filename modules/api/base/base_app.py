import fastapi
import fastapi.middleware.cors
import pymongo.collection

import base.config


def create_base_app() -> fastapi.FastAPI:
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
            "http://localhost:30002",
            "http://localhost:30003",
            "http://localhost:30004",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return uda_app


async def person_collection() -> pymongo.collection.Collection:
    mongo_client: pymongo.MongoClient = pymongo.MongoClient(
        base.config.MONGO_CONNECTION_URI
    )
    mongo_db = mongo_client[base.config.MONGO_DB_NAME]
    return mongo_db["person"]


async def location_collection() -> pymongo.collection.Collection:
    mongo_client: pymongo.MongoClient = pymongo.MongoClient(
        base.config.MONGO_CONNECTION_URI
    )
    mongo_db = mongo_client[base.config.MONGO_DB_NAME]
    return mongo_db["location"]
