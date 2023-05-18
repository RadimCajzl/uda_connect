FROM python:3.10-alpine

WORKDIR api

RUN python -m pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

EXPOSE 5000

COPY base base
COPY connection_tracker_grpc connection_tracker_grpc
COPY location_api location_api

CMD ["poetry" , "run", "uvicorn", "location_api.location_api:uda_app", "--host", "0.0.0.0", "--reload", "--port", "5000"]