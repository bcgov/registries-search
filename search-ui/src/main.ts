// External
import { createApp } from 'vue'
import Hotjar from 'vue-hotjar'

// Local
import App from '@/App.vue'
import { createVueRouter } from '@/router'
import store from '@/store'
import { fetchConfig, initLdClient } from '@/utils'
import vuetify from './plugins/vuetify'

// Styles
import '@mdi/font/css/materialdesignicons.min.css' // ensure you are using css-loader
import '@/assets/styles/base.scss'
import '@/assets/styles/layout.scss'
import '@/assets/styles/overrides.scss'

import KeycloakService from '@/sbc-common-components/services/keycloak.services'

declare const window: any

// main code
async function start() {
  console.info('Version', process.env.VUE_APP_VERSION)
  // fetch config from environment and API
  // must come first as inits below depend on config
  await fetchConfig()

  const app = createApp(App)

  // configure Keycloak Service
  console.info('Starting Keycloak service...') // eslint-disable-line no-console
  const keycloakConfig: any = {
    url: `${window['keycloakAuthUrl']}`,
    realm: `${window['keycloakRealm']}`,
    clientId: `${window['keycloakClientId']}`
  }

  await KeycloakService.setKeycloakConfigUrl(keycloakConfig)

  // initialize Launch Darkly
  if (window.ldClientId) {
    await initLdClient()
  }

  const router = createVueRouter()

  // Initialize Hotjar
  if (window['hotjarId']) {
    console.info('Initializing Hotjar...') // eslint-disable-line no-console
    app.use(Hotjar, { id: window['hotjarId'], isProduction: true })
  }

  // start Vue application
  console.info('Starting app...') // eslint-disable-line no-console
  app.use(router).use(store).use(vuetify).mount('#app')
}

start().catch(error => {
  console.error(error) // eslint-disable-line no-console
  alert(
    'There was an error starting this page. (See console for details.)\n' +
      'Please try again later.'
  )
})
