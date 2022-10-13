FROM python:3.10

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /project
COPY poetry.lock pyproject.toml /project/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction
RUN poetry run python -m spacy download en_core_web_lg

COPY . /project

EXPOSE 3000
CMD poetry run gunicorn -w=2 -b=0.0.0.0:3000 --timeout=0 -k=gevent 'hal9000.routes:app'
