// External
import { createApp } from 'vue'
// Local
import App from '@/App.vue'
import { router } from '@/router'
import store from '@/store'
import { fetchConfig } from '@/utils'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'

// main code
async function start() {
  // fetch config from environment and API
  // must come first as inits below depend on config
  await fetchConfig()

  // start Vue application
  console.info('Starting app...') // eslint-disable-line no-console
  createApp(App).use(router).use(store).use(vuetify).mount('#app')
}

loadFonts()
start().catch(error => {
  console.error(error) // eslint-disable-line no-console
  alert(
    'There was an error starting this page. (See console for details.)\n' +
      'Please try again later.'
  )
})
