import pymongo.collection

from app.udaconnect.models import Location


class LocationService:
    def __init__(self, location_collection: pymongo.collection.Collection) -> None:
        self.location_collection = location_collection

    def create(self, location: Location) -> Location:
        self.location_collection.insert_one(location)
        return location
