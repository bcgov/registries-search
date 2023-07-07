/* eslint-disable no-console, @typescript-eslint/no-explicit-any */
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

  const borApiUrl: string =
    process.env.VUE_APP_BOR_API_URL + process.env.VUE_APP_BOR_API_VERSION + '/'
  sessionStorage.setItem('BOR_API_URL', borApiUrl)
  console.info('Set BOR API URL to: ' + borApiUrl)

  const borApiKey: string = process.env.VUE_APP_BOR_API_KEY
  if (borApiKey) {
    (<any>window).borApiKey = borApiKey
    console.info('Set BOR API key.')
  }

  const registryUrl: string = process.env.VUE_APP_REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)
  console.info('Set REGISTRY URL to: ' + registryUrl)

  // for system alert banner (sbc-common-components)
  const statusApiUrl: string =
    process.env.VUE_APP_STATUS_API_URL + process.env.VUE_APP_STATUS_API_VERSION
  sessionStorage.setItem('STATUS_API_URL', statusApiUrl)
  console.info('Set Status API URL to: ' + statusApiUrl)

  // needed for sbc common
  const authApiUrl: string = process.env.VUE_APP_AUTH_API_URL +
    process.env.VUE_APP_AUTH_API_VERSION + '/'
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)
  console.info('Set Auth API URL to: ' + authApiUrl)

  // for sbc header (sbc-common-components)
  const authWebUrl: string = process.env.VUE_APP_AUTH_WEB_URL
  sessionStorage.setItem('AUTH_WEB_URL', authWebUrl)
  console.info('Set Auth Web URL to: ' + authWebUrl)

  // for business search redirect
  const registriesSearchUrl: string = process.env.VUE_APP_REGISTRIES_SEARCH_URL
  sessionStorage.setItem('REGISTRIES_SEARCH_URL', registriesSearchUrl)
  console.info('Set REGISTRIES SEARCH URL to: ' + registriesSearchUrl)

  const keycloakAuthUrl: string = process.env.VUE_APP_KEYCLOAK_AUTH_URL;
  (<any>window).keycloakAuthUrl = keycloakAuthUrl

  const keycloakRealm: string = process.env.VUE_APP_KEYCLOAK_REALM;
  (<any>window).keycloakRealm = keycloakRealm

  const keycloakClientId: string = process.env.VUE_APP_KEYCLOAK_CLIENTID;
  (<any>window).keycloakClientId = keycloakClientId

  const ldClientId: string = process.env.VUE_APP_BOR_LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
    console.info('Set Launch Darkly Client ID.')
  }

  const sentryDsn = process.env.VUE_APP_SENTRY_DSN
  if (sentryDsn) {
    (<any>window).sentryDsn = sentryDsn
    console.info('Set Sentry DSN.')
  }

  const sentryTSR = process.env.VUE_APP_SENTRY_TRACE_SAMPLE_RATE
  if (sentryTSR) {
    (<any>window).sentryTSR = sentryDsn
    console.info('Set Sentry Trace Sample Rate to', sentryTSR)
  }

  const hotjarId: string = process.env.VUE_APP_HOTJAR_ID
  if (hotjarId) {
    (<any>window).hotjarId = hotjarId
    console.info('Set HotJar ID.')
  }
  // set Base for Vue Router
  // eg, "/basePath/xxxx/"
  const vueRouterBase = processEnvBaseUrl
  sessionStorage.setItem('VUE_ROUTER_BASE', vueRouterBase)
  console.info('Set Vue Router Base to: ' + vueRouterBase)

  // set Base URL for returning from redirects
  // eg, http://localhost:8080/basePath/xxxx/
  const baseUrl = origin + vueRouterBase
  sessionStorage.setItem('BASE_URL', baseUrl)
  console.info('Set Base URL to: ' + baseUrl)

  const podNamespace = process.env.VUE_APP_POD_NAMESPACE
  sessionStorage.setItem('POD_NAMESPACE', podNamespace)
  console.info('POD_NAMESPACE: ' + podNamespace)
}
