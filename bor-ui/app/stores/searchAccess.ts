/** Manages search access data */
export const useSearchAccessStore = defineStore('searchAccess', () => {
  const productStore = useAccountProductStore()
  const accessLevel = ref(SearchAccess.PUBLIC)
  const hasExtendedAccess = computed(() => accessLevel.value === SearchAccess.EXTENDED)
  const hasLimitedAccess = computed(() => accessLevel.value === SearchAccess.LIMITED)
  const hasPublicAccess = computed(() => accessLevel.value === SearchAccess.PUBLIC)

  const init = async () => {
    if (!productStore.activeProducts.length) {
      await productStore.setActiveProducts()
    }
    await setUserAccessLevel()
  }

  /** Set access level of based on available user / account information. */
  const setUserAccessLevel = async () => {
    console.info('Setting user access to search...')
    const ldarkly = useConnectLaunchDarkly()
    // NOTE: if it is possible ldarkly was not initialized successfully (i.e. blank/incorrect key)
    const productStore = useAccountProductStore()

    if (
      ldarkly.getStoredFlag<boolean>('enable-comp-auth-search').value
      || productStore.hasProductAccess(ProductCode.CA_SEARCH)
    ) {
      // set search as competent authority search
      accessLevel.value = SearchAccess.EXTENDED
      console.info('Set to Competent Authority Search.')
    } else if (
      ldarkly.getStoredFlag<boolean>('enable-director-search').value
      || productStore.hasProductAccess(ProductCode.NDS)
    ) {
      // set search as director search
      accessLevel.value = SearchAccess.LIMITED
      console.info('Set to Director Search.')
    } else {
      console.info('Set to Public Search.')
    }
  }

  const $reset = () => {
    productStore.$reset()
    accessLevel.value = SearchAccess.PUBLIC
  }

  return {
    accessLevel,
    hasExtendedAccess,
    hasLimitedAccess,
    hasPublicAccess,
    init,
    $reset
  }
})
