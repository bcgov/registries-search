## Dependencies
1. Oracle database (COLIN data load)
2. Postgres database (LEAR data load)
3. Solr connection (data import)

## Setup
Clone the repo and submit a PR from a new branch.

### Install the dependencies
```bash
poetry install
```

### Configure the .env
(see .env.sample)

```bash
eval $(poetry env activate)
```

### Run the importer
```bash
python data_import_handler.py
```

### Run Linting
```bash
ruff check --fix
```

### Run unit tests
```bash
pytest
```
