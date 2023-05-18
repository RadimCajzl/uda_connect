"""Basic grpc server for connection tracking.

Given one person-location, time and spatial limits, returns
list of possible connections.

Boilerplate code taken from Udacity gRPC example from and adjusted:
https://github.com/udacity/nd064-c2-message-passing-exercises/blob/master/lesson-3-implementing-message-passing/grpc-demo/main.py
"""


import datetime as dt
import time
from concurrent import futures

import grpc
import pymongo

import app.config
import app.udaconnect.models
import connection_tracker_api.connection_pb2
import connection_tracker_api.connection_pb2_grpc
from app.udaconnect.connection_tracker import ConnectionTracker

mongo_client: pymongo.MongoClient = pymongo.MongoClient(app.config.MONGO_CONNECTION_URI)
mongo_db = mongo_client[app.config.MONGO_DB_NAME]


class ConnectionTrackerAPI(
    connection_tracker_api.connection_pb2_grpc.ConnectionTrackerServicer
):
    def Get(self, request, context):
        ## Parse input
        source_location = app.udaconnect.models.Location.from_grpc(request.location)
        start_date = dt.datetime.fromisoformat(request.start_date)
        end_date = dt.datetime.fromisoformat(request.end_date)
        meters = int(request.meters)

        ## Find connections
        connection_tracker = ConnectionTracker(
            person_collection=mongo_db["person"],
            location_collection=mongo_db["location"],
        )
        connections = connection_tracker.find_contacts_one_location(
            location=source_location,
            start_date=start_date,
            end_date=end_date,
            meters=meters,
        )

        ## Encode response
        grpcio_connections = [
            one_connection.to_grpc() for one_connection in connections
        ]
        return iter(grpcio_connections)


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    connection_tracker_api.connection_pb2_grpc.add_ConnectionTrackerServicer_to_server(
        ConnectionTrackerAPI(), server
    )

    print(f"Server starting on port {app.config.CONNECTION_TRACKER_PORT}.")
    server.add_insecure_port(f"[::]:{app.config.CONNECTION_TRACKER_PORT}")
    server.start()
    # Keep thread alive
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
