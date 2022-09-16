FROM python:3.10

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /project
COPY poetry.lock pyproject.toml /project/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction

COPY . /project

EXPOSE 3000
CMD poetry run flask --app=hal9000 --port=3000
