const { defineConfig } = require('@vue/cli-service')

process.env.VUE_APP_VERSION = process.env.npm_package_version
// NB: uncomment to run in production mode
// process.env.NODE_ENV = "production"

module.exports = defineConfig({
  transpileDependencies: true,

  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    },
  },
  publicPath: `${process.env.VUE_APP_PATH}`
})
