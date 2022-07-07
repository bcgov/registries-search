### Dependencies
1. Oracle database (COLIN data load)
2. Postgres database (LEAR data load)
3. Solr connection (data import)

### Development Setup
1. run `make setup`
2. create your .env based on .env.sample
3. run the importer
  - `./run.sh` OR
  - `python data_import_handler.py`
