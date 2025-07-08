import { LDPlugin } from 'launchdarkly-vue-client-sdk'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(LDPlugin, { deferInitialization: true })
})
