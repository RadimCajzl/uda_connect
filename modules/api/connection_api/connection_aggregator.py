from datetime import datetime
from typing import List

import grpc  # type: ignore
import pymongo.collection

import base.config
import connection_tracker_grpc.connection_pb2_grpc
from base.models import Connection, Location


class ConnectionAggregator:
    def __init__(
        self,
        person_collection: pymongo.collection.Collection,
        location_collection: pymongo.collection.Collection,
    ) -> None:
        self.person_collection = person_collection
        self.location_collection = location_collection

    def find_contacts(
        self, person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """

        locations = [
            Location.parse_obj(one_location)
            for one_location in self.location_collection.find(
                {
                    "person_id": person_id,
                    "creation_time": {"$lt": end_date, "$gte": start_date},
                }
            )
        ]

        connection_tracker_channel = grpc.insecure_channel(
            base.config.CONNECTION_TRACKER_GRPC_URL
        )
        connection_tracker_client = (
            connection_tracker_grpc.connection_pb2_grpc.ConnectionTrackerStub(
                connection_tracker_channel
            )
        )

        result: List[Connection] = list()
        # TODO: this for cycle should be parallelized for better performance.
        for this_person_location in locations:
            grpc_connections_one_location = connection_tracker_client.Get(
                connection_tracker_grpc.connection_pb2.ConnectionRequest(  # type: ignore
                    location=this_person_location.to_grpc(),
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    meters=meters,
                )
            )
            for one_grpc_connection in grpc_connections_one_location:
                result.append(Connection.from_grcp(one_grpc_connection))

        return result
