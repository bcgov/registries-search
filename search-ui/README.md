[![Lifecycle:Retired](https://img.shields.io/badge/Lifecycle-Retired-d45500)](<Redirect-URL>)

> [!WARNING]
> **ARCHIVED / DEPRECATED**
> This directory contains legacy code and is no longer maintained.
>
> **Replacement:** See [`bor-ui`](https://github.com/bcgov/person-search/tree/main/bor-ui) for the active implementation.

# search-ui

## Project configuration
- node 16
- vue/cli 5.0.4
- vue 3
- vuetify 3
- vuex
- vue composition api (non class component style)
- typescript
- jest
- eslint


## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your unit tests
```
npm run test:unit
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
});
