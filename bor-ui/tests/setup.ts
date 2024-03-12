import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { testAccount, testProducts, testUser } from './test-utils'

export const vuetify = createVuetify({
  components,
  directives
})

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
      activeProducts: ref(testProducts),
      userAccounts: ref(testProducts),
      userFirstName,
      userLastName,
      userFullName: ref(`${userFirstName.value} ${userLastName.value}`),
      accountErrors: ref([]),
      getAuthUserProfile: () => null,
      hasProductAccess: () => true,
      setActiveProducts: (val: any) => console.info(val)
    }
  }
})
