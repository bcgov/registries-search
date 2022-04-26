const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,

  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    },
  },
  devServer: {
    proxy: {
      // this is needed to prevent a CORS error when running locally
      '/local-keycloak-config-url/*': {
        target: 'https://dev.bcregistry.ca/business/config/kc/',
        pathRewrite: {
          '/local-keycloak-config-url': ''
        }
      },
      // this is needed to avoid a PAYBC Not Found error when running locally
      '/status/PAYBC': {
        target: 'https://status-api-dev.apps.silver.devops.gov.bc.ca/api/v1/status/PAYBC',
        pathRewrite: {
          '/status/PAYBC': ''
        }
      }
    }
  }
})
