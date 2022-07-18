import { computed, reactive } from 'vue'
// bc registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { ErrorCategories, ErrorCodes, ProductCode, ProductStatus, StaffRoles, UserRoles } from '@/enums'
import { AuthI, CurrentAccountI } from '@/interfaces'
import { getAccountProducts, getSbcFromAuth } from '@/requests'
import keycloakServices from '@/sbc-common-components/services/keycloak.services'
import { getKeycloakRoles } from '@/utils'

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
    // check if product code in activeProducts or if staff access enables product code
    if (isStaff.value || isStaffHelpDesk.value || isStaffPPR.value) return true
    const product = auth.activeProducts.find(product => product.code === code)
    if (!product) return false
    return true
  }
  const isStaff = computed(() => auth.staffRoles.includes(StaffRoles.STAFF))
  const isStaffHelpDesk = computed(() => auth.staffRoles.includes(StaffRoles.HELP_DESK))
  const isStaffPPR = computed(() => auth.staffRoles.includes(StaffRoles.PPR))
  const isStaffSBC = computed(() => auth.staffRoles.includes(StaffRoles.SBC))
  const loadAuth = async () => {
    // set current account / set staff roles / get active products
    await _loadRoles()
    await _loadCurrentAccount()
    // check sbc
    if (auth.userRoles.includes(UserRoles.GOV_ACCOUNT)) {
      const isSbc = await getSbcFromAuth()
      if (isSbc) auth.staffRoles.push(StaffRoles.SBC)
    }
    if (!isStaff.value && !isStaffHelpDesk.value && !isStaffPPR.value) await _loadProducts()
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
    let currentAccount = ''
    // TODO: need to change '0' to something recognized as staff by auth
    // and agreed upon within search / gateway and validate on the backend accordingly
    if (isStaff.value || isStaffHelpDesk.value || isStaffPPR.value) currentAccount = '{"id":"0"}'
    else currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
    if (!currentAccount) console.error(`Error: session ${SessionStorageKeys.CurrentAccount} expected, but not found.`)
    auth.currentAccount = JSON.parse(currentAccount) as CurrentAccountI
  }
  const _loadProducts = async () => {
    // get/set active products
    try {
      const products = await getAccountProducts()
      auth.activeProducts = products.filter(product => product.subscriptionStatus === ProductStatus.ACTIVE)
    } catch (error) {
      console.error(error)
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
      console.error(error)
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
    isStaffHelpDesk,
    isStaffPPR,
    isStaffSBC,
    loadAuth,
    startTokenService
  }
}