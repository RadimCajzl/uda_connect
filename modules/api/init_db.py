import pathlib
from typing import List

import pydantic
import pymongo
import pymongo.errors

import app.config as uda_config
import app.udaconnect.models as uda_models

print("Initializing UdaConnect MongoDB.")

root_data_path = pathlib.Path(__file__).parent

people = [
    one_person.dict()
    for one_person in pydantic.parse_file_as(
        List[uda_models.Person], root_data_path / "person.json"
    )
]
locations = [
    one_location.dict()
    for one_location in pydantic.parse_file_as(
        List[uda_models.Location], root_data_path / "location.json"
    )
]

print("Data loaded.")

mongo_client: pymongo.MongoClient = pymongo.MongoClient(uda_config.MONGO_CONNECTION_URI)
mongo_db = mongo_client[uda_config.MONGO_DB_NAME]
people_collection = mongo_db["person"]
locations_collection = mongo_db["location"]

try:
    people_collection.insert_many(people)
    print("People data inserted.")
except pymongo.errors.BulkWriteError:
    print("Skipping people data insertion, already exists.")


try:
    locations_collection.insert_many(locations)
except pymongo.errors.BulkWriteError:
    print("Skipping location data insertion, already exists.")


people_collection.create_index("id", unique=True)
locations_collection.create_index("id", unique=True)
locations_collection.create_index([("coordinates", pymongo.GEOSPHERE)])

print("Unique custom ID-fields, geo index created.")

print("UdaConnect MongoDB initialized successfully.")
