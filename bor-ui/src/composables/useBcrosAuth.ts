import type { KeycloakConfig } from 'keycloak-js'

/** Manages auth flows */
export const useBcrosAuth = () => {
  const config = useRuntimeConfig()
  const keycloak = useBcrosKeycloak()
  const account = useBcrosAccount()
  const { redirect, goToSetupAccount, goToCreateAccount } = useBcrosNavigate()

  /** redirect to the correct creation screen based on auth state */
  function createAccount () {
    if (keycloak.kc.authenticated) {
      goToSetupAccount()
    } else {
      goToCreateAccount()
    }
  }

  /** Logout and then redirect to given page (if redirect provided). */
  async function logout (redirect: string) { await keycloak.logout(redirect) }

  /** redirect if account status is suspended */
  function verifyAccountStatus () {
    const accountStatus = account.currentAccount?.accountStatus
    if (accountStatus) {
      if ([AccountStatusE.NSF_SUSPENDED, AccountStatusE.SUSPENDED].includes(accountStatus)) {
        redirect(`${config.public.authWebURL}/account-freeze`)
      } else if (accountStatus === AccountStatusE.PENDING_STAFF_REVIEW) {
        const accountName = encodeURIComponent(btoa(account.currentAccountName || ''))
        redirect(`${config.public.authWebURL}/pendingapproval/${accountName}/true`)
      }
    }
  }

  /** Setup keycloak / user auth pieces */
  async function setupAuth (kcConfig: KeycloakConfig, currentAccountId?: string) {
    if (!keycloak.kc.authenticated) {
      console.info('Initializing auth setup...')
      // initialize keycloak with user token
      console.info('Initializing Keycloak...')
      try {
        await keycloak.initKeyCloak(kcConfig)
        if (keycloak.kc.authenticated) {
          // successfully initialized so setup other pieces
          keycloak.syncSessionStorage()
          keycloak.scheduleRefreshToken()
          // set user info
          console.info('Setting user name...')
          await account.setUserName()
          // set account info
          console.info('Setting user account information...')
          await account.setAccountInfo(Number(currentAccountId))
          // check account status
          console.info('Checking account status...')
          // verify account status
          verifyAccountStatus()
          console.info('Auth setup complete.')
        }
      } catch (error) {
        console.warn('Keycloak initialization failed:', error)
      }
    }
  }

  return {
    createAccount,
    logout,
    setupAuth
  }
}
