import { computed, reactive } from 'vue'
// bc registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { AccountTypes, ErrorCategories, ErrorCodes, ProductCode, ProductStatus, StaffRoles, UserRoles } from '@/enums'
import { AuthI, CurrentAccountI } from '@/interfaces'
import { getAccountProducts } from '@/requests'
import keycloakServices from '@/sbc-common-components/services/keycloak.services'
import { getKeycloakName, getKeycloakRoles, updateLdUser } from '@/utils'

const auth = reactive({
  activeProducts: [],
  currentAccount: null,
  staffRoles: [],
  tokenInitialized: false,
  userRoles: [],
  _error: null
} as AuthI)

export const useAuth = () => {
  // manager for auth + common functions etc.
  const hasProductAccess = (code: ProductCode) => {
    // check if product code in activeProducts
    const product = auth.activeProducts.find(product => product.code === code)
    if (!product) return false
    return true
  }
  const isStaff = computed(() => auth.currentAccount?.accountType === AccountTypes.STAFF)
  const isStaffSBC = computed(() => auth.currentAccount?.accountType === AccountTypes.SBC_STAFF)
  const loadAuth = async () => {
    // set current account / set staff roles / get active products
    await _loadRoles()
    if (!auth._error) await _loadCurrentAccount()
    if (!auth._error) await _loadProducts()
    // update ldarkly user
    if (!auth._error) await updateLdUser(auth.currentAccount.name, '', '', '')
  }
  /** Starts token service that refreshes KC token periodically. */
  const startTokenService = async () => {
    // only initialize once
    if (auth.tokenInitialized) return
    try {
      console.info('Starting token refresh service...')
      await keycloakServices.initializeToken()
      auth.tokenInitialized = true
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
  const _clearAuth = () => {
    auth.activeProducts = []
    auth.currentAccount = null
    auth.staffRoles = []
    auth.tokenInitialized = false
    auth._error = null
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
      auth._error = {
        category: ErrorCategories.ACCOUNT_SETTINGS,
        message: 'Error getting/setting current account.',
        statusCode: null,
        type: ErrorCodes.ACCOUNT_SETUP_ERROR
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
      auth._error = {
        category: ErrorCategories.ACCOUNT_ACCESS,
        message: 'Error getting/setting active user products.',
        statusCode: null,
        type: ErrorCodes.AUTH_PRODUCTS_ERROR
      }
    }
  }
  const _loadRoles = async () => {
    // get/set staff roles (add in user roles here if needed)
    try {
      const roles = getKeycloakRoles()
      const userRoleList = Object.values(UserRoles)
      const userRoles = roles.filter(role => userRoleList.includes(role as UserRoles))
      auth.userRoles = userRoles as UserRoles[]
      const staffRoleList = Object.values(StaffRoles)
      const staffRoles = roles.filter(role => staffRoleList.includes(role as StaffRoles))
      auth.staffRoles = staffRoles as StaffRoles[]
    } catch (error) {
      console.warn(error)
      auth._error = {
        category: ErrorCategories.ACCOUNT_ACCESS,
        message: 'Error getting/setting auth roles.',
        statusCode: null,
        type: ErrorCodes.AUTH_ROLES_ERROR
      }
    }
  }
  return {
    auth,
    hasProductAccess,
    isStaff,
    isStaffSBC,
    loadAuth,
    startTokenService
  }
}