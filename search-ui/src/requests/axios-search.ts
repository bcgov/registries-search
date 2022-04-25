// External
import Axios from 'axios'
import * as Sentry from '@sentry/vue'
// BC registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

const axiosSearch = Axios.create()

// insert common headers used for all search-api requests
axiosSearch.interceptors.request.use(
  (config) => {
    if (!config?.headers) throw new Error('config.headers does not exist.')
    // FUTURE: not sure if we need to make this config.headers.common.Authorization (for now shows typescript error)
    config.headers.Authorization = `Bearer ${sessionStorage.getItem(
      SessionStorageKeys.KeyCloakToken
    )}`
    return config
  },
  (error) => Promise.reject(error)
)

// FUTURE: only send specific errors to sentry
axiosSearch.interceptors.response.use(
  (response) => response,
  (error) => {
    Sentry.captureException(error)
    return Promise.reject(error)
  }
)

export { axiosSearch }
