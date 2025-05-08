
[![License](https://img.shields.io/badge/License-Apache%20bsd-3.svg)](LICENSE)


# Application Name

BC Registries Search Solr Updater

## Documentation

This service is used to update the search solr core after a business change event.
It's a bridge between lear -> search-solr via queue, based on events.

## Technology Stack Used
* Python, Flask
* GCP Pub/Sub

## Development Setup

### Windows Development Pre-Setup

Follow the instructions of the [Development Readme](https://github.com/bcgov/entity/blob/master/docs/development.md)
to setup your local development environment.

### Setup
Clone the repo and create a new branch.

Set to use the local repo for the virtual environment
```bash
poetry config virtualenvs.in-project true
```
Install the dependencies
```bash
poetry install
```

Configure the .env (see .env.sample)

### Run the service
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

## License

   Copyright © 2025 Province of British Columbia

   Licensed under the BSD 3 Clause License, (the "License");
   you may not use this file except in compliance with the License.
   The template for the license can be found here
      https://opensource.org/license/bsd-3-clause/

   Redistribution and use in source and binary forms,
   with or without modification, are permitted provided that the
   following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

   3. Neither the name of the copyright holder nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.

