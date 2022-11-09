.PHONY: cd

PROJECT_NAME=search-solr

#################################################################################
# COMMANDS - CD
#################################################################################
cd: ## CD flow
ifeq ($(TAG_NAME), test)
cd: echo 'n/a'
else ifeq ($(TAG_NAME), prod)
cd: echo 'n/a'
else
TAG_NAME=dev
cd: build tag
endif

build: ## Build the new compute image
	gcloud compute instances list --filter name:search-solr --sort-by NAME --format=json --project $(PROJECT_ID) > instances.json; \
	gcloud compute instances create search-solr-base-$(NEW_VERSION) --source-instance-template search-solr-base --zone $(ZONE) --project $(PROJECT_ID); \
	gcloud compute instances stop search-solr-base-$(NEW_VERSION) --zone $(ZONE) --project $(PROJECT_ID); \
	gcloud compute images create search-solr-$(NEW_VERSION) --family search-solr --source-disk search-solr-base-$(NEW_VERSION) --project $(PROJECT_ID); \
	gcloud compute instance-groups unmanaged list-instances search-solr-preload-grp-$(TAG_NAME) --zone=$(ZONE) --format=json --project $(PROJECT_ID) > instances_in_preload.json; \
	instances_in_preload=$(jq -r '.[].name' instances_in_preload.json); \
	instances_to_rmv=$instances_in_preload | tr ' ' ,; \
	gcloud compute instance-groups unmanaged remove-instances search-solr-preload-grp-$(TAG_NAME) --zone=$(ZONE) --instances=$instances_to_rmv
	gcloud compute instance-groups unmanaged add-instances search-solr-preload-grp-$TAG_NAME --zone=$ZONE --instances=search-solr-$(TAG_NAME)-$(NEW_VERSION)

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################
.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
