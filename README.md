# Registries Search
BC Registry's business search service
## search-ui
UI portion for registries search. Contains user facing registries searching and results components.
## search-api
Makes calls to solr for search, calls to lear apps, etc. for business data, and puts payments on the queue.
## search-solr
Reused the bcgov/namex solr instance and added a new 'search' core for this project.
- To contribute to it you can update https://github.com/bcgov/namex/tree/main/solr/cores/search
- To update the solr build or run it locally checkout https://github.com/bcgov/namex-solr.git
## search-solr-feeder
Adds new businesses / updates businesses in solr when they are created/changed in bcgov/lear.
## search-pay-listener
Listens for completed search payments and updates the search db via the search-api model.
## Developer contirbution flow
setup
1. fork this repo
2. locally clone your forked repo
3. locally set upstream to this repo: 
- `git remote add upstream https://github.com/bcgov/registries-search.git`
4. locally prevent pushing to upstream
- `git remote set-url --push upstream no_push`
5. verify
- `git remote -v`

contribute
1. checkout upstream/main
2. switch to new branch *ticket_number*-*description*
3. make changes + ensure linter/tests pass
4. commit / push to your forked repo
- `git push origin <branch_name>`
5. PR your forked repo changes to this repo
6. assign yourself to the PR and add reviewers
