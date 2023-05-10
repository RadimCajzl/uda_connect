from datetime import datetime
from typing import List

from app.udaconnect.models import Connection, Location, Person, UdaMongoCollections


class ConnectionService:
    def __init__(self, mongo_collections: UdaMongoCollections) -> None:
        self.person_collection = mongo_collections.person
        self.location_collection = mongo_collections.location

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


class LocationService:
    def __init__(self, mongo_collections: UdaMongoCollections) -> None:
        self.person_collection = mongo_collections.person
        self.location_collection = mongo_collections.location

    def create(self, location: Location) -> Location:
        self.location_collection.insert_one(location)
        return location


class PersonService:
    def __init__(self, mongo_collections: UdaMongoCollections) -> None:
        self.person_collection = mongo_collections.person
        self.location_collection = mongo_collections.location

    def create(self, person: Person) -> Person:
        self.person_collection.insert_one(person)

        return person

    def retrieve(self, person_id: int) -> Person:
        if (
            person_data := self.person_collection.find_one({"id": person_id})
        ) is not None:
            return Person.parse_obj(person_data)
        else:
            raise ValueError(f"No {person_id = } found in database.")

    def retrieve_all(self) -> List[Person]:
        return [
            Person.parse_obj(one_person) for one_person in self.person_collection.find()
        ]
