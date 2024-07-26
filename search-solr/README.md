# Application Name

BC Registries Registry Search SOLR

## Technology Stack Used

- Apache Solr
- Docker

### Development Setup

1. Pull the base solr docker image

- `docker pull solr:9.6.1`

2. Run your solr containers

- if first time or need to pickup new solr changes outside of /solr/business directory:
  - Build leader image: `make build-local`
  - Run leader image: `docker run -d -p 8873:8983 --name business-solr-leader-local business-solr-local` (it will be available on port 8873)
    _NOTE: if you want the data to persist then add `-v $PWD/solr/business:/var/solr/data` (do NOT do this for the solr instance used for api unit tests)_
  - Optional: setup follower node
    - Get leader IP: `docker inspect business-solr-leader-local | grep IPAddress`
    - Use the docker IP to set the leader url: `export LEADER_URL=http://leader_IP:8873/solr/business`
    - Build the follower image: `make build-follower`
    - Run follower image: `docker run -d -p 8884:8984 --name business-solr-follower-local business-solr-follower` (it will be available on port 8884)
    - Add docker network so that follower can poll from leader:
      - `docker network create solr`
      - `docker network connect solr business-solr-leader-local`
      - `docker network connect solr business-solr-follower-local`
- else
  - `docker start business-solr-leader-local`

3. Check logs for errors

- `docker logs business-solr-leader-local`

4. Go to admin UI in browser and check the solr core is there (it will be empty)

- http://localhost:8873/solr
