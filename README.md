# Registries Search
BC Registry's business search service
## search-ui
UI portion for registries search. Contains user facing registries searching and results components.
## search-api
Makes calls to solr for search, calls to lear apps, etc. for business data, and stores payments/access rights for documents.
## search-solr
Indexes / queries our business data.
## search-solr-importer
Adds new businesses / updates businesses in solr from COLIN and LEAR.
## doc-service
Stores point in time documents (i.e. business summary)
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
