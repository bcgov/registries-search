// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
// Vuetify
import { createVuetify } from 'vuetify'

export default createVuetify({
  iconfont: 'mdi',
  theme: {
    defaultTheme: 'bcgov',
    themes: {
      bcgov: {
        colors: {
          primary: '#1669bb', // same as $$primary-blue
          darkBlue: '#38598a',
          error: '#d3272c',
          success: '#1a9031',
          warning: '#ffc107'
        }
      }
    },
  },
})
// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
