import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default defineNuxtPlugin((nuxtApp) => {
  const vuetify = createVuetify({
    ssr: true,
    components,
    directives,
    icons: {
      defaultSet: 'mdi'
    },
    theme: {
      defaultTheme: 'bcgov',
      themes: {
        bcgov: {
          colors: {
            primary: '#1669bb', // same as $$app-blue
            darkBlue: '#38598a',
            error: '#d3272c',
            success: '#1a9031',
            warning: '#ffc107'
          }
        }
      }
    }
  })
  nuxtApp.vueApp.use(vuetify)
})
