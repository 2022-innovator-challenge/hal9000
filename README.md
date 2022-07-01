# HAL9000

This is a NLP-based GitHub bot using [spaCy](https://spacy.io/).

## Development

It is recommended to use `pyenv`.

1. Install [poetry](https://python-poetry.org/docs/)
2. Install [rust](https://www.rust-lang.org/tools/install)
3. Download vectors from [sense2vec](https://github.com/explosion/sense2vec) and save in folder vectors
4. Run the following commands

```
pip install -U pip
poetry install
poetry run python -m spacy download en_core_web_lg
poetry run hal9000 <ISSUE_NUMBER>
```

### Format & Lint

```
poetry run black .
poetry run pyright
poetry run prospector
```
