import { computed, reactive } from 'vue'
// bc registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { AccountTypes, ErrorCategories, ErrorCodes } from '@/enums'
import { AuthI, CurrentAccountI, ErrorI } from '@/interfaces'
import keycloakServices from '@/sbc-common-components/services/keycloak.services'
import { getKeycloakName, updateLdUser } from '@/utils'

// read only globals (export directly for tests only)
export const _readOnly = reactive({
  error: null as ErrorI,
  tokenInitialized: false
})

// global state TODO: try moving to pinia
const auth = reactive({
  currentAccount: null,
  _error: computed(() => _readOnly.error),
  _tokenInitialized: computed(() => _readOnly.tokenInitialized)
} as AuthI)

// private functions used internally
const _clearAuth = () => {
  auth.currentAccount = null
  _readOnly.error = null
  _readOnly.tokenInitialized = false
}

const _loadCurrentAccount = async () => {
  try {
    const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
    // parse/set current account info
    if (!currentAccount) console.error(`Error: session ${SessionStorageKeys.CurrentAccount} expected, but not found.`)
    auth.currentAccount = JSON.parse(currentAccount) as CurrentAccountI
    // set user name
    auth.currentAccount.name = getKeycloakName()
  } catch (error) {
    console.warn(error)
    _readOnly.error = {
      category: ErrorCategories.ACCOUNT_SETTINGS,
      message: 'Error getting/setting current account.',
      statusCode: null,
      type: ErrorCodes.ACCOUNT_SETUP_ERROR
    }
  }
}

export const useAuth = () => {
  // manager for auth + common functions etc.
  const isStaff = computed(() => auth.currentAccount?.accountType === AccountTypes.STAFF)
  const isStaffSBC = computed(() => auth.currentAccount?.accountType === AccountTypes.SBC_STAFF)
  const loadAuth = async () => {
    // set current account
    if (!auth._error) await _loadCurrentAccount()
    // update ldarkly user
    if (!auth._error) await updateLdUser(auth.currentAccount.name, '', '', '')
  }
  /** Starts token service that refreshes KC token periodically. */
  const startTokenService = async () => {
    // clear existing errors
    _readOnly.error = null
    // only initialize once
    if (auth._tokenInitialized) return
    try {
      console.info('Starting token refresh service...')
      await keycloakServices.initializeToken()
      _readOnly.tokenInitialized = true
    } catch (e) {
      // this happens when the refresh token has expired
      // 1. clear flags and keycloak data
      _clearAuth()
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakToken)
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakRefreshToken)
      sessionStorage.removeItem(SessionStorageKeys.KeyCloakIdToken)
      sessionStorage.removeItem(SessionStorageKeys.CurrentAccount)
      // 2. reload app to get new tokens
      location.reload()
    }
  }
  return {
    auth,
    isStaff,
    isStaffSBC,
    loadAuth,
    startTokenService
  }
}