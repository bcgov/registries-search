export default defineNuxtConfig({
  app: {
    buildAssetsDir: '/src/',
    head: {
      title: 'Business and Person Search',
      htmlAttrs: { dir: 'ltr' },
      link: [{ rel: 'icon', type: 'image/ico', href: '/favicon.ico' }]
    }
  },
  colorMode: {
    preference: 'light',
    fallback: 'light',
    storageKey: 'nuxt-color-mode'
  },
  devtools: { enabled: true },
  srcDir: 'src/',
  css: [
    '@mdi/font/css/materialdesignicons.css',
    '@/assets/styles/base.scss',
    '@/assets/styles/layout.scss'
  ],
  ssr: false,
  imports: {
    dirs: ['enums', 'interfaces', 'stores']
  },
  modules: [
    '@nuxt/ui',
    '@nuxtjs/i18n',
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    // Skip GTM and GTag modules for cypress test environment
    ...(process.env.CYPRESS ? [] : ['@zadigetvoltaire/nuxt-gtm', 'nuxt-gtag'])
  ],
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
  gtm: {
    enabled: !!process.env.VUE_APP_GTM_ID?.trim(),
    id: process.env.VUE_APP_GTM_ID?.trim() as string || 'GTM-DUMMY', // the dummy value allows app to run if GTM ID in not loaded
    debug: true,
    defer: true
  },
  gtag: {
    enabled: !!process.env.VUE_APP_GTAG_ID?.trim(),
    id: process.env.VUE_APP_GTAG_ID?.trim()
  },
  runtimeConfig: {
    public: {
      // Keys within public, will be also exposed to the client-side
      authApiURL: `${process.env.VUE_APP_AUTH_API_URL || ''}${process.env.VUE_APP_AUTH_API_VERSION || ''}`,
      authWebURL: process.env.VUE_APP_AUTH_WEB_URL || '',
      kcURL: process.env.VUE_APP_KEYCLOAK_AUTH_URL || '',
      kcRealm: process.env.VUE_APP_KEYCLOAK_REALM || '',
      kcClient: process.env.VUE_APP_KEYCLOAK_CLIENTID || '',
      ldClientId: process.env.VUE_APP_BOR_LD_CLIENT_ID || '',
      legalApiURL: `${process.env.VUE_APP_LEGAL_API_URL || ''}${process.env.VUE_APP_LEGAL_API_VERSION_2 || ''}`,
      borApiURL: `${process.env.VUE_APP_BOR_API_URL || ''}${process.env.VUE_APP_BOR_API_VERSION || ''}`,
      borApiKey: `${process.env.VUE_APP_BOR_API_KEY || ''}`,
      regSearchApiURL: `${process.env.VUE_APP_REGISTRIES_SEARCH_API_URL || ''}` +
        `${process.env.VUE_APP_REGISTRIES_SEARCH_API_VERSION || ''}`,
      regSearchApiURLV2: `${process.env.VUE_APP_REGISTRIES_SEARCH_API_URL || ''}` +
        `${process.env.VUE_APP_REGISTRIES_SEARCH_API_VERSION_2 || ''}`,
      regSearchApiKey: `${process.env.VUE_APP_REGISTRIES_SEARCH_API_KEY || ''}`,
      registryHomeURL: process.env.VUE_APP_REGISTRY_HOME_URL || '',
      bcolURL: process.env.VUE_APP_BCONLINE_URL || '',
      businessDashURL: process.env.VUE_APP_BUSINESS_DASH_URL || '',
      businessSearchURL: process.env.VUE_APP_REGISTRIES_SEARCH_URL || '',
      appEnv: `${process.env.VUE_APP_POD_NAMESPACE || 'unknown'}`,
      requireLogin: true,
      searchRows: `${process.env.VUE_APP_SEARCH_ROWS || ''}`,
      version: process.env.npm_package_version || '',
      appName: process.env.npm_package_name || '',
      appNameDisplay: 'BCROS Search'
    }
  }
})
