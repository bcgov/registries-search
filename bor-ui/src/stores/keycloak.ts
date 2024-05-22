import Keycloak from 'keycloak-js'
import type { KeycloakConfig, KeycloakInitOptions, KeycloakLoginOptions } from 'keycloak-js'

/** Default interval (seconds) for checking if the user token needs to be refreshed. */
const DEFAULT_REFRESH_CHECK_INTERVAL = 60

/** Default minimum time (seconds) before expiry for refreshing the user token. */
const DEFAULT_REFRESH_MIN_VALIDITY = 120

/** Manages bcros keycloak authentication service data and flows */
export const useBcrosKeycloak = defineStore('bcros/keycloak', () => {
  const kc: Ref<Keycloak> = ref({} as Keycloak)

  const kcUser = computed((): KCUserI => {
    if (kc.value?.tokenParsed) {
      return {
        firstName: kc.value.tokenParsed.firstname,
        lastName: kc.value.tokenParsed.lastname,
        fullName: kc.value.tokenParsed.name,
        userName: kc.value.tokenParsed.username,
        email: kc.value.tokenParsed.email,
        keycloakGuid: kc.value.tokenParsed.sub || '',
        loginSource: kc.value.tokenParsed.loginSource,
        roles: kc.value.tokenParsed.realm_access?.roles || []
      }
    }
    return {} as KCUserI
  })
  const kcUserKeycloakGuid = computed(() => kcUser.value.keycloakGuid)
  const kcUserLoginSource = computed(() => kcUser.value.loginSource)
  const kcUserRoles = computed(() => kcUser.value.roles || [])

  function clearSession () {
    kc.value = {} as Keycloak
    sessionStorage.removeItem(SessionStorageKeyE.KEYCLOAK_TOKEN)
    sessionStorage.removeItem(SessionStorageKeyE.KEYCLOAK_TOKEN_REFRESH)
    sessionStorage.removeItem(SessionStorageKeyE.KEYCLOAK_TOKEN_ID)
    sessionStorage.removeItem(SessionStorageKeyE.KEYCLOAK_SYNCED)
  }

  function syncSessionStorage () {
    if (!kc.value) {
      sessionStorage.setItem(SessionStorageKeyE.KEYCLOAK_SYNCED, 'false')
      return
    }
    sessionStorage.setItem(SessionStorageKeyE.KEYCLOAK_TOKEN, kc.value?.token || '')
    sessionStorage.setItem(SessionStorageKeyE.KEYCLOAK_TOKEN_REFRESH, kc.value?.refreshToken || '')
    sessionStorage.setItem(SessionStorageKeyE.KEYCLOAK_TOKEN_ID, kc.value?.idToken || '')
    sessionStorage.setItem(SessionStorageKeyE.KEYCLOAK_SYNCED, 'true')
  }

  async function initKeyCloak (
    config: KeycloakConfig,
    token?: string,
    refreshToken?: string,
    idToken?: string,
    idpHint?: string,
    forceLogin?: boolean
  ) {
    kc.value = new Keycloak(config)
    if (kc.value) {
      // add idpHint to login options
      const kcLogin = kc.value.login
      kc.value.login = function (options?: KeycloakLoginOptions) {
        if (options) {
          options.idpHint = idpHint
        }
        return kcLogin(options)
      }

      kc.value.onTokenExpired = function () {
        kc.value?.updateToken(300)
        syncSessionStorage()
      }
    }
    const kcOptions: KeycloakInitOptions = {
      onLoad: forceLogin ? 'login-required' : 'check-sso',
      timeSkew: 0,
      token: token || undefined,
      refreshToken: refreshToken || undefined,
      idToken: idToken || undefined,
      pkceMethod: 'S256',
      responseMode: 'query'
    }
    return await kc.value.init(kcOptions)
  }

  /** Schedule refreshing the token regularly. */
  function scheduleRefreshToken (
    timeout = DEFAULT_REFRESH_CHECK_INTERVAL,
    minValidity = DEFAULT_REFRESH_MIN_VALIDITY
  ) {
    setTimeout(() => {
      if (kc.value?.isTokenExpired(minValidity)) {
        console.info('Token set to expire soon. Refreshing token...')
        kc.value?.updateToken(minValidity)
        syncSessionStorage()
        console.info('Token updated.')
        scheduleRefreshToken(timeout, minValidity)
      }
    }, timeout)
  }

  async function logout (redirect: string) {
    await kc.value?.logout({ redirectUri: redirect })
    clearSession()
  }

  return {
    kc,
    kcUser,
    kcUserKeycloakGuid,
    kcUserLoginSource,
    kcUserRoles,
    initKeyCloak,
    scheduleRefreshToken,
    syncSessionStorage,
    logout
  }
})
