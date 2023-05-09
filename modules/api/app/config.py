import os

MONGO_CONNECTION_URI = os.environ["MONGO_CONNECTION_URI"]
MONGO_DB_NAME = "connections"

DEBUG = os.environ["DEBUG"].lower() == "true"
