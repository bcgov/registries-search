export default defineNuxtConfig({
  app: {
    buildAssetsDir: '/src/',
    head: {
      htmlAttrs: { dir: 'ltr' },
      link: [{ rel: 'icon', type: 'image/ico', href: '/src/assets/images/favicon.ico' }]
    }
  },
  devtools: { enabled: true },
  srcDir: 'src/',
  css: [
    '@mdi/font/css/materialdesignicons.css',
    '@/assets/styles/base.scss',
    '@/assets/styles/layout.scss'
  ],
  ui: {
    icons: ['mdi']
  },
  ssr: false,
  imports: {
    dirs: ['enums', 'interfaces', 'stores']
  },
  modules: ['@nuxt/ui', '@nuxtjs/i18n', '@pinia/nuxt', '@nuxtjs/tailwindcss'],
  typescript: {
    tsConfig: {
      compilerOptions: {
        noImplicitAny: false,
        strictNullChecks: false,
        strict: true
      }
    },
    // NOTE: https://github.com/vuejs/language-tools/issues/3969
    typeCheck: false
  },
  i18n: {
    lazy: true,
    defaultLocale: 'en',
    langDir: './lang',
    locales: [
      { code: 'en', file: 'en.json' }
    ]
  },
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
      bcolURL: process.env.VUE_APP_BCONLINE_URL || '',
      businessSearchURL: process.env.VUE_APP_REGISTRIES_SEARCH_URL || '',
      appEnv: `${process.env.VUE_APP_POD_NAMESPACE || 'unknown'}`,
      requireLogin: process.env.VUE_APP_REQUIRE_LOGIN === 'true' || false,
      searchRows: `${process.env.VUE_APP_SEARCH_ROWS || ''}`,
      version: process.env.npm_package_version || ''
    }
  }
})
