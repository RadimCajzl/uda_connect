from kafka import KafkaProducer  # type: ignore

import base.config
from base.models import Location


class LocationCollector:
    def __init__(self) -> None:
        self.kafka_producer = KafkaProducer(bootstrap_servers=base.config.KAFKA_SERVER)
        self.kafka_topic = base.config.KAFKA_TOPIC

    def _send(self, message: bytes) -> None:
        self.kafka_producer.send(self.kafka_topic, message)
        self.kafka_producer.flush()

    def create(self, location: Location) -> Location:
        self._send(location.json().encode())
        return location
