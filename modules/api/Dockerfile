FROM python:3.10-alpine

WORKDIR api

RUN python -m pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

EXPOSE 5000

COPY . .

CMD ["poetry" , "run", "uvicorn", "main:uda_app", "--host", "0.0.0.0", "--reload", "--port", "5000"]