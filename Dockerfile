FROM python:3.9

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE = false

RUN pip install poetry

COPY ["poetry.lock", "pyproject.toml", "/app/"]

RUN poetry install --no-ansi --no-interaction

COPY . /app

VOLUME /app/storage

CMD ["python", "main.py"]