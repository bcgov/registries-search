# registries-search
BC Registry's business search service
## search-ui
UI portion for registries search. Contains user facing registries searching and results components.
## search-api
Makes calls to solr for search, calls to lear apps, etc. for business data, and puts payments on the queue.
## search-solr
Registries search solr cores + indexes. (may not need this if re-using namex solr setup + adding a core / new indexes there)
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
