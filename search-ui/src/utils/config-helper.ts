/**
 * Fetches config from environment and API.
 * @returns A promise to get & set session storage keys with appropriate values.
 */
export async function fetchConfig(): Promise<any> {
  // get config from environment
  const origin: string = window.location.origin // eg, http://localhost:8080
  const processEnvVueAppPath: string = process.env.VUE_APP_PATH
  const processEnvBaseUrl: string = process.env.BASE_URL // /

  if (!origin || !processEnvVueAppPath || !processEnvBaseUrl) {
    return Promise.reject(new Error('Missing environment variables'))
  }

  const searchApiUrl: string =
    process.env.VUE_APP_REGISTRIES_SEARCH_API_URL + process.env.VUE_APP_REGISTRIES_SEARCH_API_VERSION + '/'
  sessionStorage.setItem('REGISTRY_SEARCH_API_URL', searchApiUrl)

  const searchApiKey: string = process.env.VUE_APP_REGISTRIES_SEARCH_API_KEY
  if (searchApiKey) {
    (<any>window).searchApiKey = searchApiKey
  }

  const registryUrl: string = process.env.VUE_APP_REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)

   // for system alert banner (sbc-common-components)
  const statusApiUrl: string =
    process.env.VUE_APP_STATUS_API_URL + process.env.VUE_APP_STATUS_API_VERSION
  sessionStorage.setItem('STATUS_API_URL', statusApiUrl)

  // for sbc header (sbc-common-components)
  const authWebUrl: string = process.env.VUE_APP_AUTH_WEB_URL
  sessionStorage.setItem('AUTH_WEB_URL', authWebUrl)

  const entityWebUrl: string = process.env.VUE_APP_DASHBOARD_URL
  sessionStorage.setItem('DASHBOARD_URL', entityWebUrl)

  const authApiUrl: string = process.env.VUE_APP_AUTH_API_URL + process.env.VUE_APP_AUTH_API_VERSION + '/'
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)

  const legalApiUrl: string = process.env.VUE_APP_LEGAL_API_URL + process.env.VUE_APP_LEGAL_API_VERSION_2 + '/'
  sessionStorage.setItem('LEGAL_API_URL', legalApiUrl)

  const payApiUrl: string = process.env.VUE_APP_PAY_API_URL + process.env.VUE_APP_PAY_API_VERSION + '/'
  sessionStorage.setItem('PAY_API_URL', payApiUrl)

  const ldClientId: string = process.env.VUE_APP_LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
  }

  const sentryDsn = process.env.VUE_APP_SENTRY_DSN
  if (sentryDsn) {
    (<any>window).sentryDsn = sentryDsn
  }

  const sentryTSR = process.env.VUE_APP_SENTRY_TRACE_SAMPLE_RATE
  if (sentryTSR) {
    (<any>window).sentryTSR = sentryTSR
  }

  const hotjarId: string = process.env.VUE_APP_HOTJAR_ID
  if (hotjarId) {
    (<any>window).hotjarId = hotjarId
  }

  const keycloakAuthUrl: string = process.env.VUE_APP_KEYCLOAK_AUTH_URL;
  (<any>window).keycloakAuthUrl = keycloakAuthUrl

  const keycloakRealm: string = process.env.VUE_APP_KEYCLOAK_REALM;
  (<any>window).keycloakRealm = keycloakRealm

  const keycloakClientId: string = process.env.VUE_APP_KEYCLOAK_CLIENTID;
  (<any>window).keycloakClientId = keycloakClientId

  // set Base for Vue Router
  // eg, "/basePath/xxxx/"
  const vueRouterBase = processEnvBaseUrl
  sessionStorage.setItem('VUE_ROUTER_BASE', vueRouterBase)

  // set Base URL for returning from redirects
  // eg, http://localhost:8080/basePath/xxxx/
  const baseUrl = origin + vueRouterBase
  sessionStorage.setItem('BASE_URL', baseUrl)

  const podNamespace = process.env.VUE_APP_POD_NAMESPACE
  sessionStorage.setItem('POD_NAMESPACE', podNamespace)
}
