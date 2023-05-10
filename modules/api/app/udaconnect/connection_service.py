from datetime import datetime
from typing import List

import pymongo.collection

from app.udaconnect.models import Connection, Location, Person


class ConnectionService:
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

        result: List[Connection] = list()
        for this_person_location in locations:
            one_location_connections = [
                Connection(
                    person=Person.parse_obj(
                        self.person_collection.find_one(
                            {"id": other_person_location["person_id"]}
                        )
                    ),
                    location=Location.parse_obj(other_person_location),
                )
                for other_person_location in self.location_collection.find(
                    {
                        "id": {"$ne": person_id},
                        "creation_time": {"$lt": end_date, "$gte": start_date},
                        "coordinates": {
                            "$near": {
                                "$geometry": {
                                    "type": "Point",
                                    "coordinates": this_person_location.coordinates,
                                },
                                "$maxDistance": meters,
                            }
                        },
                    }
                )
            ]
            result += one_location_connections

        return result
