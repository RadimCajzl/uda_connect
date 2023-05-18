FROM python:3.10-alpine

WORKDIR api

RUN python -m pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

EXPOSE 5000

COPY base base
COPY connection_tracker_grpc connection_tracker_grpc
COPY connection_tracker connection_tracker

COPY connection_tracker_api.py .
CMD ["poetry" , "run", "python", "connection_tracker_api.py"]