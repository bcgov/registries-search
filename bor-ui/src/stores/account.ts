import Axios from 'axios'
import { StatusCodes } from 'http-status-codes'
import type { ProductCodeE } from '#imports'

/** Manages bcros account data */
export const useBcrosAccount = defineStore('bcros/account', () => {
  // keycloak info
  const keycloak = useBcrosKeycloak()
  // selected user account
  const currentAccount: Ref<AccountI> = ref({} as AccountI)
  const currentAccountName = computed((): string => currentAccount.value?.label || '')
  const activeProducts: Ref<ProductI[]> = ref([])
  // user info
  const user = computed(() => keycloak.kcUser)
  const userAccounts: Ref<AccountI[]> = ref([])
  const userFirstName: Ref<string> = ref(user.value?.firstName || '-')
  const userLastName: Ref<string> = ref(user.value?.lastName || '')
  const userFullName = computed(() => `${userFirstName.value} ${userLastName.value}`)
  // errors
  const accountErrors: Ref<ErrorI[]> = ref([])
  // api request variables
  const axios = addAxiosInterceptors(Axios.create())
  const apiURL = useRuntimeConfig().public.authApiURL

  /** Get user information from AUTH */
  async function getAuthUserProfile (identifier: string) {
    return await axios.get<KCUserI | void>(`${apiURL}/users/${identifier}`)
      .then((response) => {
        const data = response?.data
        if (!data) { throw new Error('Invalid AUTH API response') }
        return data
      })
      .catch((error) => {
        console.warn('Error fetching user info.')
        accountErrors.value.push({
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategoryE.USER_INFO
        })
      })
  }

  /** Update user information in AUTH with current token info */
  async function updateAuthUserInfo () {
    return await axios.post<KCUserI | void>(`${apiURL}/users`, { isLogin: true })
      .then(response => response.data)
      .catch((error) => {
        // not too worried if this errs -- log for ops
        console.error('Error updating Auth with login attempt', error)
      })
  }

  /** Set user name information */
  async function setUserName () {
    if (user.value?.loginSource === LoginSourceE.BCEID) {
      // get from auth
      const authUserInfo = await getAuthUserProfile('@me')
      if (authUserInfo) {
        userFirstName.value = authUserInfo.firstName
        userLastName.value = authUserInfo.lastName
      }
      return
    }
    userFirstName.value = user.value?.firstName || '-'
    userLastName.value = user.value?.lastName || ''
  }

  /** Get the user's account list */
  // eslint-disable-next-line
  async function getUserAccounts (keycloakGuid: string) {
    return axios.get<UserSettingsI[]>(`${apiURL}/users/${keycloakGuid}/settings`)
      .then((response) => {
        const data = response?.data
        if (!data) { throw new Error('Invalid AUTH API response') }
        return data.filter(userSettings => (userSettings.type === UserSettingsTypeE.ACCOUNT)) as AccountI[]
      })
      .catch((error) => {
        console.warn('Error fetching user settings / account list.')
        accountErrors.value.push({
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategoryE.ACCOUNT_LIST
        })
      })
  }

  /** Get all the current account products. */
  async function getAccountProducts (): Promise<ProductI[]> {
    const config = { baseURL: apiURL, params: { include_hidden: true } }
    return await axios.get<ProductI[]>(`orgs/${currentAccount.value?.id}/products`, config)
      .then((response) => {
        const data = response?.data
        if (!data) { throw new Error('Invalid API response') }
        return data
      })
      .catch((error) => {
        console.info(error)
        throw new Error('Error fetching account products, status code = ' +
          error?.response?.status?.toString() || StatusCodes.NOT_FOUND.toString())
      })
  }

  /** Check if the current account has the product. */
  function hasProductAccess (code: ProductCodeE) {
    // check if product code in activeProducts
    return !!activeProducts.value?.find(product => product.code === code)
  }

  /** Set the active products for the current account. */
  async function setActiveProducts () {
    try {
      const products = await getAccountProducts()
      activeProducts.value = products.filter(product => product.subscriptionStatus === ProductStatusE.ACTIVE)
    } catch (error) {
      console.warn(error)
      accountErrors.value.push({
        category: ErrorCategoryE.ACCOUNT_ACCESS,
        message: 'Error getting/setting active user products.',
        statusCode: null,
        type: ErrorCodeE.AUTH_PRODUCTS_ERROR
      })
    }
  }

  /** Set the user account list and current account */
  async function setAccountInfo (currentAccountId?: number) {
    if (!currentAccountId) {
      // try getting id from existing session storage
      currentAccountId = JSON.parse(sessionStorage.getItem(SessionStorageKeyE.CURRENT_ACCOUNT) || '{}').id
    }
    if (user.value?.keycloakGuid) {
      userAccounts.value = await getUserAccounts(user.value?.keycloakGuid) || []
      if (userAccounts && userAccounts.value.length > 0) {
        currentAccount.value = userAccounts.value[0]
        if (currentAccountId) {
          // if previous current account id selection information available set this as current account
          currentAccount.value = userAccounts.value.find(account => account.id === currentAccountId) || {} as AccountI
        }
        sessionStorage.setItem(SessionStorageKeyE.CURRENT_ACCOUNT, JSON.stringify(currentAccount.value))
      }
    }
  }

  /** Switch the current account to the given account ID if it exists in the user's account list */
  function switchCurrentAccount (accountId: number) {
    for (const i in userAccounts.value) {
      if (userAccounts.value[i].id === accountId) {
        currentAccount.value = userAccounts.value[i]
      }
    }
    sessionStorage.setItem(SessionStorageKeyE.CURRENT_ACCOUNT, JSON.stringify(currentAccount.value))
  }

  return {
    currentAccount,
    currentAccountName,
    userAccounts,
    userFullName,
    accountErrors,
    activeProducts,
    updateAuthUserInfo,
    setUserName,
    setAccountInfo,
    setActiveProducts,
    hasProductAccess,
    switchCurrentAccount
  }
})
