# Application Name

BC Registries Registry Search SOLR

## Technology Stack Used
* bitnami/solr
* Docker

### Development Setup
1. Pull the bitnami solr docker image
  - `docker pull bitnami/solr:latest`
2. Run your solr container
  - `docker run -d -p 8983:8983 -v /<YOUR_PATH_TO_THIS_REPO>/registries-search/search-solr/bitnami:/bitnami --name solr-local bitnami/solr:latest`
3. Check logs for errors
  - `docker logs solr-local`
4. Go to admin UI in browser and check the solr core is there (it will be empty)
  - http://localhost:8983/solr
5. Data import via the solr importer with REINDEX=True
  - see https://github.com/bcgov/registries-search/tree/main/search-solr-importer and you will need:
    - run local COLIN oracle db OR setup VPN connection to COLIN dev OR comment out the COLIN load
    - run local LEAR db OR port-forward to dev instance OR comment out LEAR load
6. Stop the solr instance, make changes and reindex / rebuild the suggester
  - `docker stop solr-local`
  - make changes
  - `docker start solr-local`
  - reimport data with REINDEX=True (5.)

