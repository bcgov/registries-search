import { mockNuxtImport } from '@nuxt/test-utils/runtime'

import { testAccount, testUser } from './test-utils'

mockNuxtImport('useBcrosNavigate', () => {
  return () => {
    return {
      goToBcrosDashboard: () => { console.info('goToBcrosDashboard') }
    }
  }
})

mockNuxtImport('useBcrosKeycloak', () => {
  // set these so the app allows entry during the tests
  return () => {
    return {
      kc: { authenticated: true },
      kcUser: { ...testUser }
    }
  }
})

mockNuxtImport('useBcrosAccount', () => {
  // set these so the header values don't err and app init doesn't fail
  return () => {
    const user = computed(() => useBcrosKeycloak().kcUser)
    const userFirstName = computed(() => user.value?.firstName || '-')
    const userLastName = computed(() => user.value?.lastName || '')
    return {
      currentAccount: ref({ ...testAccount }),
      currentAccountName: ref(testAccount.label),
      activeProducts: ref([]),
      userAccounts: ref([{ ...testAccount }]),
      userFirstName,
      userLastName,
      userFullName: ref(`${userFirstName.value} ${userLastName.value}`),
      accountErrors: ref([]),
      getAuthUserProfile: () => null,
      hasProductAccess: () => false,
      setActiveProducts: (val: any) => console.info(val)
    }
  }
})
