from datetime import datetime
from typing import List

import pymongo.collection

from app.udaconnect.models import Connection, Location, Person


class ConnectionTracker:
    def __init__(
        self,
        person_collection: pymongo.collection.Collection,
        location_collection: pymongo.collection.Collection,
    ) -> None:
        self.person_collection = person_collection
        self.location_collection = location_collection

    def find_contacts_one_location(
        self, location: Location, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """Returns all possible contacts for {location}."""

        return [
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
                    "id": {"$ne": location.person_id},
                    "creation_time": {"$lt": end_date, "$gte": start_date},
                    "coordinates": {
                        "$near": {
                            "$geometry": {
                                "type": "Point",
                                "coordinates": location.coordinates,
                            },
                            "$maxDistance": meters,
                        }
                    },
                }
            )
        ]
