import Axios from 'axios'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

const axios = Axios.create()

axios.interceptors.request.use(
  config => {
    config.headers.common['Authorization'] = `Bearer ${sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)}`
    return config
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => response,
  error => {
    console.warn(error)
    return Promise.reject(error)
  }
)

export { axios }
