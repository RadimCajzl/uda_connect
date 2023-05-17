from __future__ import annotations

import datetime as dt
from typing import Dict, Literal, Tuple

from pydantic import BaseModel

import connection_tracker_api.connection_pb2


class Person(BaseModel):
    id: int
    first_name: str
    last_name: str
    company_name: str

    def to_grpc(self):
        return connection_tracker_api.connection_pb2.Person(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            company_name=self.company_name,
        )

    @classmethod
    def from_grpc(cls, grpc_request):
        return cls(
            id=grpc_request.id,
            first_name=grpc_request.first_name,
            last_name=grpc_request.last_name,
            company_name=grpc_request.company_name,
        )


class Location(BaseModel):
    id: int
    person_id: int
    coordinates: Tuple[float, float]
    creation_time: dt.datetime

    def to_grpc(self):
        return connection_tracker_api.connection_pb2.Location(
            id=self.id,
            person_id=self.person_id,
            coordinates=list(self.coordinates),
            creation_time=self.creation_time.isoformat(),
        )

    @classmethod
    def from_grpc(cls, grpc_request) -> Location:
        return cls(
            id=grpc_request.id,
            person_id=grpc_request.person_id,
            coordinates=tuple(grpc_request.coordinates),  # type: ignore
            creation_time=grpc_request.creation_time,
        )


class Connection(BaseModel):
    location: Location
    person: Person

    def to_grpc(self):
        return connection_tracker_api.connection_pb2.Connection(
            location=self.location.to_grpc(), person=self.person.to_grpc()
        )

    @classmethod
    def from_grcp(cls, grpc_request) -> Connection:
        return cls(
            location=Location.from_grpc(grpc_request.location),
            person=Person.from_grpc(grpc_request.person),
        )


class ConnectionCountInterval(BaseModel):
    count: int
    start: dt.datetime
    duration: dt.timedelta


class ApiMetrics(BaseModel):
    status: Literal["healthy"]
    intervals: Dict[Literal["current", "previous"], ConnectionCountInterval | None]
