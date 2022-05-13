# HAL9000

This is a NLP-based GitHub bot using [spaCy](https://spacy.io/).

## Development

It is recommended to use `pyenv`.

1. Install [poetry](https://python-poetry.org/docs/)
2. Install [rust](https://www.rust-lang.org/tools/install)
3. Run the following commands

```
pip install -U pip
poetry install
poetry run python -m spacy download en_core_web_trf
```

### Format & Lint

```
poetry run black .
poetry run pyright
poetry run prospector
```
