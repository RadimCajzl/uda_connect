import logging
import os

MONGO_CONNECTION_URI = os.environ["MONGO_CONNECTION_URI"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]

CONNECTION_TRACKER_PORT = int(os.environ["CONNECTION_TRACKER_PORT"])
CONNECTION_TRACKER_GRPC_URL = (
    f"{os.environ['CONNECTION_TRACKER_HOST']}:{os.environ['CONNECTION_TRACKER_PORT']}"
)

KAFKA_SERVER = os.environ["KAFKA_SERVER"]
KAFKA_TOPIC = "locations"

DEBUG = os.getenv("DEBUG") == "True"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
