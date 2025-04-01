# Application Name

BC Registries Registry Search API

## Background

For API usage documentation see _TBD_
For BC Registries Gateway API configuration see [Gateway Search Proxy](https://github.com/bcregistry/apigw/blob/master/proxy/README-ppr.md)

## Technology Stack Used

- Python, Flask
- Postgres - SQLAlchemy, psycopg2-binary & alembic
- SOLR
- Poetry

## Development Setup

### Windows Development Pre-Setup

Follow the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

### Setup
Clone the repo and submit a PR from a new branch.

Set to use the local repo for the virtual environment
```bash
poetry config virtualenvs.in-project true
```
Install the dependencies
```bash
poetry install
```

Configure the .env (see .env.sample)

### Setup the DB
Run a local instance of the Postgres BOR database.
   1. Pull postgres image from docker
   1. `docker run --name local-db -e POSTGRES_PASSWORD=tiger -d -p 5432:5432 postgres`
   1. `docker exec -it local-db psql -U postgres -W postgres`
   1. create a database for development and a database for unit tests
   1. update your .env DATABASE_NAME/DATABASE_TEST_NAME/PASSWORD values to match
   1. upgrade the db
      ```bash
      eval $(poetry env activate)
      ```

      NOTE: Default COMMAND is 'upgrade' and 'REVISION' is optional
      ```bash
      ./update_db.sh $COMMAND $REVISION
      ```

### Run the search-api
```bash
eval $(poetry env activate)
```

```bash
flask run -p 5000
```

### Run Linting
```bash
eval $(poetry env activate)
```
```bash
ruff check --fix
```

### Run Unit Tests

- Ensure you have the following setup/configured:
   - test database
   - test solr instance or set RUN_SOLR_TESTS=False
      - default config points to docker-compose.yml
      - see https://github.com/bcgov-registries/beneficial-ownership/tree/main/bor-solr for more info on *bor-solr-leader* image
- ```
   eval $(poetry env activate)
   ```
- For all unit tests:
   ```
   pytest
   ```
- For an individual file:
   ```
   pytest tests/unit/api/filename.py 
   ```
- For an individual test case:
   ```
   pytest tests/unit/api/filename.py::test-case-name
   ```

### Run Integration (postman) Tests

1. Start your local application(s).
2. Open postman applicaiton.
3. Import the [Integration tests environment configrations](./tests/postman/bor-api-LOCAL.postman_environment.json) and fill the values to match your applicaiton.
4. Import the [integration tests collection](./tests/postman/bor-api.postman_collection.json).
5. Run the collection.

## How to Contribute

If you would like to contribute, please see our [CONTRIBUTING](./CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md).
By participating in this project you agree to abide by its terms.

## License

    Copyright 2022 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
