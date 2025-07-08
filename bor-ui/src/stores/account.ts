import { StatusCodes } from 'http-status-codes'
import type { KCUserI, ProductCodeE } from '#imports'

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
  const apiURL = useRuntimeConfig().public.authApiURL

  /** Get user information from AUTH */
  async function getAuthUserProfile (identifier: string) {
    return await useBcrosFetch<any>(`${apiURL}/users/${identifier}`)
      .then(({ data, error }) => {
        if (error.value || !data.value) {
          console.warn('Error fetching user info.', error.value)
          accountErrors.value.push({
            statusCode: error.value?.status || StatusCodes.INTERNAL_SERVER_ERROR,
            message: error.value?.data?.message,
            category: ErrorCategoryE.USER_INFO
          })
        }
        if (data.value.firstname) {
          data.value.firstName = data.value.firstname
        }
        if (data.value.lastname) {
          data.value.lastName = data.value.lastname
        }
        return data.value as KCUserI
      })
  }

  /** Update user information in AUTH with current token info */
  async function updateAuthUserInfo () {
    return await useBcrosFetch<KCUserI>(`${apiURL}/users`, { method: 'POST', body: { isLogin: true } })
      .then(({ data, error }) => {
        if (error.value || !data.value) {
          // not too worried if this errs -- log for ops
          console.error('Error updating Auth with login attempt', error)
        }
        return data.value
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
  async function getUserAccounts (keycloakGuid: string) {
    return await useBcrosFetch<UserSettingsI[]>(`${apiURL}/users/${keycloakGuid}/settings`)
      .then(({ data, error }) => {
        if (error.value || !data.value) {
          console.warn('Error fetching user settings / account list.', error.value)
          accountErrors.value.push({
            statusCode: error.value?.status || StatusCodes.INTERNAL_SERVER_ERROR,
            message: error.value?.data?.message,
            category: ErrorCategoryE.ACCOUNT_LIST
          })
          return
        }
        return data.value.filter(userSettings => (userSettings.type === UserSettingsTypeE.ACCOUNT)) as AccountI[]
      })
  }

  /** Get all the current account products. */
  async function getAccountProducts (): Promise<ProductI[]> {
    const config = { baseURL: apiURL, params: { include_hidden: true } }
    return await useBcrosFetch<ProductI[]>(`orgs/${currentAccount.value?.id}/products`, config)
      .then(({ data, error }) => {
        if (error.value || !data.value) {
          console.info(error)
          accountErrors.value.push({
            statusCode: error.value?.status || StatusCodes.INTERNAL_SERVER_ERROR,
            message: error.value?.data?.message,
            category: ErrorCategoryE.ACCOUNT_PRODUCTS
          })
        }
        if (data.value instanceof Object) {
          return data.value
        }
        // NB: for some reason useFetch is returning this response list as a string
        return JSON.parse((data.value as unknown) as string)
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
