export default defineNuxtRouteMiddleware(async (to) => {
  // setup auth
  if (!to.query.error) {
    // keycloak redirects with the error param when not logged in (nuxt/keycloak issue)
    //   - removing ^ condition will cause an infinite loop of keycloak redirects when not authenticated
    const { kcURL, kcRealm, kcClient } = useRuntimeConfig().public
    await useBcrosAuth().setupAuth(
      { url: kcURL, realm: kcRealm, clientId: kcClient },
      to.params.currentAccountId as string || to.query.currentAccountId as string
    )
  }
})
