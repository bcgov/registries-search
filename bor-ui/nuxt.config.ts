// https://nuxt.com/docs/api/configuration/nuxt-config
// import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  devtools: { enabled: true },
  srcDir: 'src/',
  css: [
    'vuetify/lib/styles/main.sass',
    '@mdi/font/css/materialdesignicons.css',
    '@/assets/styles/base.scss',
    '@/assets/styles/layout.scss',
    '@/assets/styles/overrides.scss'
  ],
  build: {
    transpile: ['vuetify']
  },
  ssr: false,
  imports: {
    dirs: ['enums', 'interfaces', 'stores']
  },
  modules: ['@pinia/nuxt'],
  runtimeConfig: {
    public: {
      // Keys within public, will be also exposed to the client-side
      addressCompleteKey: process.env.VUE_APP_ADDRESS_COMPLETE_KEY,
      authApiURL: `${process.env.VUE_APP_AUTH_API_URL || ''}${process.env.VUE_APP_AUTH_API_VERSION || ''}`,
      authWebURL: process.env.VUE_APP_AUTH_WEB_URL || '',
      kcURL: process.env.VUE_APP_KEYCLOAK_AUTH_URL || '',
      kcRealm: process.env.VUE_APP_KEYCLOAK_REALM || '',
      kcClient: process.env.VUE_APP_KEYCLOAK_CLIENTID || '',
      ldClientId: process.env.VUE_APP_BOR_LD_CLIENT_ID || '',
      legalApiURL: `${process.env.VUE_APP_LEGAL_API_URL || ''}${process.env.VUE_APP_LEGAL_API_VERSION_2 || ''}`,
      payApiURL: `${process.env.VUE_APP_PAY_API_URL || ''}${process.env.VUE_APP_PAY_API_VERSION || ''}`,
      btrApiURL: `${process.env.VUE_APP_BTR_API_URL || ''}${process.env.VUE_APP_BTR_API_VERSION || ''}`,
      borApiURL: `${process.env.VUE_APP_BOR_API_URL || ''}${process.env.VUE_APP_BOR_API_VERSION || ''}`,
      borApiKey: `${process.env.VUE_APP_BOR_API_KEY || ''}`,
      registryHomeURL: process.env.VUE_APP_REGISTRY_HOME_URL || '',
      appEnv: `${process.env.VUE_APP_POD_NAMESPACE || 'unknown'}`,
      searchRows: `${process.env.VUE_APP_SEARCH_ROWS || ''}`,
      version: process.env.npm_package_version || ''
    }
  }
})
