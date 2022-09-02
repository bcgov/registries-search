### Dependencies
- node 16 (for converting postman files to k6 tests)
- k6 https://k6.io/docs/getting-started/installation (for running tests)

### Developer Setup
- `npm install` (only necessary if you are updating the postman tests)
- install k6: https://k6.io/docs/getting-started/installation

### Workflow
1. update postman collection / env
2. convert to k6 test file `npm convert:postman`
3. update converted file as needed (you may need to copy paste the info in the terminal into the desired test file)
4. run the test `k6 run search_full_flow.js`

### Devops notes
If you upgrade the libs folder please note that inside `libs/shim/core.js` we needed to update the fn `executeRequest` with
```
// remove unwanted saved options
delete setting.options.headers
```
before returning the response to prevent the headers of each request overwriting future request headers.
