import logging
import time

import pydantic
import pymongo.collection
import pymongo.errors
from kafka import KafkaConsumer  # type: ignore

import app.config
from app.udaconnect.models import Location

logging.basicConfig(level=app.config.LOG_LEVEL)

POLLING_TIMEOUT_MS = 1000
SLEEP_INTERVAL_S = 1  # TODO: in production, change to higher value.


class LocationProcessor:
    def __init__(self, location_collection: pymongo.collection.Collection) -> None:
        self.location_collection = location_collection

    def create(self, location: Location) -> Location:
        self.location_collection.insert_one(location.dict())
        return location


if __name__ == "__main__":
    mongo_client: pymongo.MongoClient = pymongo.MongoClient(
        app.config.MONGO_CONNECTION_URI
    )
    mongo_db = mongo_client[app.config.MONGO_DB_NAME]
    location_collection = mongo_db["location"]

    location_processor = LocationProcessor(location_collection=location_collection)

    # Infinite Kafka consumer loop, inspired by
    # https://stackoverflow.com/questions/66101466/python-kafka-keep-polling-topic-infinitely

    kafka_location_consumer = KafkaConsumer(bootstrap_servers=[app.config.KAFKA_SERVER])
    kafka_location_consumer.subscribe(app.config.KAFKA_TOPIC)

    logging.info(
        f"Polling Kafka server {app.config.KAFKA_SERVER}, topic {app.config.KAFKA_TOPIC}."
    )
    while True:
        location_message = kafka_location_consumer.poll(timeout_ms=POLLING_TIMEOUT_MS)

        if location_message:
            for location_records in location_message.values():
                for one_location_record in location_records:
                    try:
                        location = Location.parse_raw(one_location_record.value)
                        location_processor.create(location=location)
                        logging.info(f"Inserted {location = }.")
                    except pydantic.ValidationError:
                        logging.error(
                            f"Unable to parse {one_location_record.value = }, skipping."
                        )
                    except pymongo.errors.DuplicateKeyError:
                        logging.error(
                            f"Attempted to save duplicate location to db {one_location_record.value = }."
                        )
        else:
            time.sleep(SLEEP_INTERVAL_S)
            continue
