# Application Name

BC Registries Registry Search SOLR

## Technology Stack Used

- Apache Solr
- Docker

### Development Setup

1. Pull the base solr docker image

- `docker pull solr:9.10.1`

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

### VM Deployment

The Solr cluster runs on GCP Compute Engine VMs (`k973yf-<env>`). Instance templates are created/refreshed via `search-solr/create-templates.sh`; a blue-green deploy script is provided at `search-solr/deploy-vm.sh`:

- `./create-templates.sh [dev|test|prod]` — recreate the leader (and follower for test/prod) instance templates from `startupscript.txt`, backing up any existing template to `<name>-old`. Machine types and JVM heap derive from per-env values in the script.
- the deploy script creates a new leader VM (and follower for test/prod) from instance templates
- waits for the new VMs to become healthy before swapping backends
- triggers the `search-solr-importer-<env>` job in OpenShift to reindex into the new leader, pausing the sync schedulers around the import
- sets the follower's replication `leaderUrl` to the new leader's internal IP and waits for replication
- deletes the old VMs only after everything succeeds

**Prerequisites:** `gcloud` (authenticated), `oc` (authenticated), `docker`, `make`.

**Actions:**

| Command | Purpose |
| --- | --- |
| `./deploy-vm.sh build` | DEV only: build + push `business-solr-leader` / `business-solr-follower` images to `northamerica-northeast1-docker.pkg.dev/c4hnrd-tools/vm-repo` |
| `./deploy-vm.sh tag` | Tag the `dev` images for `test` / `prod` |
| `./deploy-vm.sh deploy` | Deploy new leader (DEV: leader only) or leader + follower (TEST/PROD), reindex, wire up replication |
| `./deploy-vm.sh deploy-follower` | TEST/PROD only: replace the follower against the existing leader |

**Options (deploy / deploy-follower):**

- `--leader-machine-type <type>` — override leader machine type (e.g. `e2-standard-4`)
- `--follower-machine-type <type>` — override follower machine type

**Configuration** (edit at the top of `deploy-vm.sh`):

- `ENV` — `dev` / `test` / `prod`
- `LEADER_TEMPLATE_VERSION` / `FOLLOWER_TEMPLATE_VERSION` — suffix on the base instance templates, if any (e.g. `v2`, `v8cpu`)

The instance templates, backend services (`business-solr-leader-svc-<env>` / `business-solr-follower-svc-<env>`), load balancers, instance groups and the `search-solr-importer-<env>` cronjob/secret must already exist in the respective GCP/OpenShift projects.
