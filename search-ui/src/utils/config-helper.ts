/* eslint-disable no-console, @typescript-eslint/no-explicit-any */
import Axios from 'axios'
import { getFeatureFlag } from '@/utils'

// basic axios obj used for config call
const axios = Axios.create()

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

  // fetch config from API
  // eg, http://localhost:8080/business/search/config/configuration.json
  // eg, https://dev.bcregistry.ca/business/search/config/configuration.json
  const url = `${origin}/${processEnvVueAppPath}/config/configuration.json`
  const headers = {
    Accept: 'application/json',
    ResponseType: 'application/json',
    'Cache-Control': 'no-cache',
  }

  const response = await axios.get(url, { headers }).catch(() => {
    return Promise.reject(new Error('Could not fetch configuration.json'))
  })

  const searchApiUrl: string =
    response.data.REGISTRIES_SEARCH_API_URL + response.data.REGISTRIES_SEARCH_API_VERSION + '/'
  sessionStorage.setItem('REGISTRY_SEARCH_API_URL', searchApiUrl)
  console.info('Set Registry Search API URL to: ' + searchApiUrl)

  const searchApiKey: string = response.data.REGISTRIES_SEARCH_API_KEY
  if (searchApiKey) {
    (<any>window).searchApiKey = searchApiKey
    console.info('Set Search API key.')
  }

  const registryUrl: string = response.data.REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)
  console.info('Set REGISTRY URL to: ' + registryUrl)

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

  const entityWebUrl: string = response.data.DASHBOARD_URL
  sessionStorage.setItem('DASHBOARD_URL', entityWebUrl)
  console.info('Set Entity Dashboard URL to: ' + entityWebUrl)

  const authApiUrl: string = response.data['AUTH_API_URL'] + response.data['AUTH_API_VERSION'] + '/'
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)
  console.log('Set Auth API URL to: ' + authApiUrl)

  const legalApiUrl: string = response.data['LEGAL_API_URL'] + response.data['LEGAL_API_VERSION_2'] + '/'
  sessionStorage.setItem('LEGAL_API_URL', legalApiUrl)
  console.log('Set Legal API URL to: ' + legalApiUrl)

  const payApiUrl: string = response.data.PAY_API_URL + response.data.PAY_API_VERSION + '/'
  sessionStorage.setItem('PAY_API_URL', payApiUrl)
  console.log('Set Pay API URL to: ' + payApiUrl)

  const ldClientId: string = response.data.LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
    console.info('Set Launch Darkly Client ID.')
  }

  const sentryEnable = getFeatureFlag('sentry-enable')
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

  const hotjarId: string = response.data.HOTJAR_ID
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

  const podNamespace = response.data.POD_NAMESPACE
  sessionStorage.setItem('POD_NAMESPACE', podNamespace)
  console.info('POD_NAMESPACE: ' + podNamespace)
}
