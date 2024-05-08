export default defineNuxtRouteMiddleware(async (to) => {
  // setup auth
  if (!to.query.error) {
    // keycloak redirects with the error param when not logged in (nuxt/keycloak issue)
    //   - removing ^ condition will cause an infinite loop of keycloak redirects when not authenticated
    const { kcURL, kcRealm, kcClient } = useRuntimeConfig().public
    await useBcrosAuth().setupAuth(
      { url: kcURL, realm: kcRealm, clientId: kcClient },
      to.params.accountid as string || to.query.accountid as string
    )
  }
  // For cypress tests. NOTE: all api calls will need to be intercepted/stubbed
  if (process.client && sessionStorage?.getItem('FAKE_CYPRESS_LOGIN') === 'true') {
    const { kc } = useBcrosKeycloak()
    // set test kc values
    kc.tokenParsed = {
      firstname: 'TestFirst',
      lastname: 'TestLast',
      name: 'TestFirst TestLast',
      username: 'testUsername',
      email: 'testEmail@test.com',
      sub: 'testSub',
      loginSource: 'IDIR',
      realm_access: { roles: ['basic'] }
    }
    kc.authenticated = true
    // set account stuff (normally would happen after kc init in 'setupAuth')
    const account = useBcrosAccount()
    await account.setUserName()
    await account.setAccountInfo()
  }
})
