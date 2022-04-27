/* eslint-disable no-console, @typescript-eslint/no-explicit-any */
import Axios from 'axios'

// basic axios obj used for config call
const axios = Axios.create()

/**
 * Fetches config from environment and API.
 * @returns A promise to get & set session storage keys with appropriate values.
 */
export async function fetchConfig(): Promise<any> {
  // get config from environment
  const origin: string = window.location.origin // eg, http://localhost:8080
  const processEnvBaseUrl = process.env.BASE_URL // /

  if (!origin || !processEnvBaseUrl) {
    return Promise.reject(new Error('Missing environment variables'))
  }

  // fetch config from API
  // eg, http://localhost:8080/config/configuration.json
  // eg, https://...-dev.apps.silver.devops.gov.bc.ca/config/configuration.json
  const url = `${origin}/config/configuration.json`
  const headers = {
    Accept: 'application/json',
    ResponseType: 'application/json',
    'Cache-Control': 'no-cache',
  }

  const response = await axios.get(url, { headers }).catch(() => {
    return Promise.reject(new Error('Could not fetch configuration.json'))
  })

  const searchApiUrl: string =
    response.data.SEARCH_API_URL + response.data.SEARCH_API_VERSION + '/'
  sessionStorage.setItem('SEARCH_API_URL', searchApiUrl)
  console.info('Set Search API URL to: ' + searchApiUrl)

  const registryUrl: string = response.data.REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)
  console.info('Set REGISTRY URL to: ' + registryUrl)

  const systemMessage: string = response.data.SYSTEM_MESSAGE
  sessionStorage.setItem('SYSTEM_MESSAGE', systemMessage)
  console.info('Set SYSTEM MESSAGE to: ' + systemMessage)

  const systemMessageType: string = response.data.SYSTEM_MESSAGE_TYPE
  sessionStorage.setItem('SYSTEM_MESSAGE_TYPE', systemMessageType)
  console.info('Set SYSTEM MESSAGE TYPE to: ' + systemMessageType)

  const keycloakConfigPath: string = response.data.KEYCLOAK_CONFIG_PATH
  sessionStorage.setItem('KEYCLOAK_CONFIG_PATH', keycloakConfigPath)
  console.info('Set Keycloak Config Path to: ' + keycloakConfigPath)

  // for system alert banner (sbc-common-components)
  const statusApiUrl: string =
    response.data.STATUS_API_URL + response.data.STATUS_API_VERSION
  sessionStorage.setItem('STATUS_API_URL', statusApiUrl)
  console.info('Set Status API URL to: ' + statusApiUrl)

  // for sbc header (sbc-common-components)
  const authWebUrl: string = response.data.AUTH_WEB_URL
  sessionStorage.setItem('AUTH_WEB_URL', authWebUrl)
  console.info('Set Auth Web URL to: ' + authWebUrl)

  const authApiUrl: string = response.data['AUTH_API_URL'] + response.data['AUTH_API_VERSION'] + '/'
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)
  console.log('Set Auth API URL to: ' + authApiUrl)

  const ldClientId: string = response.data.LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
    console.info('Set Launch Darkly Client ID.')
  }

  const sentryEnable = response.data.SENTRY_ENABLE
  ;(<any>window).sentryEnable = sentryEnable

  const sentryDsn = response.data.SENTRY_DSN
  if (sentryDsn && sentryEnable) {
    (<any>window).sentryDsn = sentryDsn
    console.info('Set Sentry DSN.')
  }

  const sentryTSR = response.data.SENTRY_TRACE_SAMPLE_RATE
  if (sentryTSR && sentryEnable) {
    (<any>window).sentryTSR = sentryDsn
    console.info('Set Sentry Trace Sample Rate to', sentryTSR)
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

  const podNamespace = response.data.POD_NAMESPACE
  sessionStorage.setItem('POD_NAMESPACE', podNamespace)
  console.info('POD_NAMESPACE: ' + podNamespace)
}
