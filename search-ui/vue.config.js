const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

process.env.VUE_APP_VERSION = process.env.npm_package_version

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    performance: {
      hints: false
    },
    optimization: {
      splitChunks: {
        minSize: 10000,
        maxSize: 250000,
      }
    },
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      })
    ],
    module: {
      rules: [
        {
          use: [
            {
              loader: 'thread-loader'
            },
            {
              loader: 'ts-loader',
              options: {
                happyPackMode: true
              }
            }
          ]
        },
      ],
    }
  },
  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    },
  },
  publicPath: `${process.env.VUE_APP_PATH}`
})
