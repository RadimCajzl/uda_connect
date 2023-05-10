import os

MONGO_CONNECTION_URI = os.environ["MONGO_CONNECTION_URI"]
MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]

DEBUG = os.getenv("DEBUG") == "True"
