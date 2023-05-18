from typing import List

import pymongo.collection

from base.models import Person


class PersonService:
    def __init__(self, person_collection: pymongo.collection.Collection) -> None:
        self.person_collection = person_collection

    def create(self, person: Person) -> Person:
        self.person_collection.insert_one(person.dict())

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
