import datetime as dt
from typing import Tuple

from pydantic import BaseModel


class Person(BaseModel):
    id: int
    first_name: str
    last_name: str
    company_name: str


class Location(BaseModel):
    id: int
    person_id: int
    coordinates: Tuple[float, float]
    creation_time: dt.datetime


class Connection(BaseModel):
    location: Location
    person: Person
