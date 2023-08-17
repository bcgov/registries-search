import { computed, reactive } from 'vue'
// bc registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { AccountType, ErrorCategory, ErrorCode, ProductCode, ProductStatus } from '@/enums'
import { AuthI, CurrentAccountI, ErrorI } from '@/interfaces'
import { getKeycloakLDValues, getKeycloakName, updateLdUser } from '@/utils'
import { getAccountProducts } from '@/requests'
import keycloakServices from '@/sbc-common-components/services/keycloak.services'

// read only globals (export directly for tests only)
export const _readOnly = reactive({
  error: null as ErrorI,
  tokenInitialized: false
})

// global state TODO: try moving to pinia
const auth = reactive({
  activeProducts: [],
  currentAccount: null,
  _error: computed(() => _readOnly.error),
  _tokenInitialized: computed(() => _readOnly.tokenInitialized)
} as AuthI)

// private functions used internally
const _clearAuth = () => {
  auth.activeProducts = []
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
      category: ErrorCategory.ACCOUNT_SETTINGS,
      message: 'Error getting/setting current account.',
      statusCode: null,
      type: ErrorCode.ACCOUNT_SETUP_ERROR
    }
  }
}

const _loadProducts = async () => {
  // get/set active products
  try {
    const products = await getAccountProducts()
    auth.activeProducts = products.filter(product => product.subscriptionStatus === ProductStatus.ACTIVE)
  } catch (error) {
    console.warn(error)
    _readOnly.error = {
      category: ErrorCategory.ACCOUNT_ACCESS,
      message: 'Error getting/setting active user products.',
      statusCode: null,
      type: ErrorCode.AUTH_PRODUCTS_ERROR
    }
  }
}

export const useAuth = () => {
  // manager for auth + common functions etc.
  const isStaff = computed(() => auth.currentAccount?.accountType === AccountType.STAFF)
  const isStaffSBC = computed(() => auth.currentAccount?.accountType === AccountType.SBC_STAFF)
  const hasProductAccess = (code: ProductCode) => {
    // check if product code in activeProducts
    const product = auth.activeProducts.find(product => product.code === code)
    if (!product) return false
    return true
  }
  const loadAuth = async () => {
    // set current account / get active products
    if (!auth._error) await _loadCurrentAccount()
    if (!auth._error) await _loadProducts()
    // update ldarkly user
    if (!auth._error) await updateLdUser(getKeycloakLDValues())
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
    hasProductAccess,
    loadAuth,
    startTokenService
  }
}