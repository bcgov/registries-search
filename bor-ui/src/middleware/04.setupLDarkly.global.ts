export default defineNuxtRouteMiddleware(() => {
  // initialize ldarkly
  useBcrosLaunchdarkly().init()
})
