/** Manages bcros search access data */
export const useBcrosSearchAccess = defineStore('bcros/searchAccess', () => {
  const accessLevel = ref(SearchAccessE.PUBLIC)
  const hasExtendedAccess = computed(() => accessLevel.value === SearchAccessE.EXTENDED)
  const hasLimitedAccess = computed(() => accessLevel.value === SearchAccessE.LIMITED)
  const hasPublicAccess = computed(() => accessLevel.value === SearchAccessE.PUBLIC)
  /** Set access level of based on available user / account information. */
  const setUserAccessLevel = async () => {
    console.info('Setting user access to search...')
    const ldarkly = useBcrosLaunchdarkly()
    // NOTE: if it is possible ldarkly was not initialized successfully (i.e. blank/incorrect key)
    await ldarkly.ldClient?.waitUntilReady()
    const account = useBcrosAccount()

    if (ldarkly.getStoredFlag('enable-comp-auth-search') || account.hasProductAccess(ProductCodeE.CA_SEARCH)) {
      // set search as competent authority search
      accessLevel.value = SearchAccessE.EXTENDED
      console.info('Set to Competent Authority Search.')
    } else if (ldarkly.getStoredFlag('enable-director-search') || account.hasProductAccess(ProductCodeE.NDS)) {
      // set search as director search
      accessLevel.value = SearchAccessE.LIMITED
      console.info('Set to Director Search.')
    } else {
      console.info('Set to Public Search.')
    }
  }

  return {
    accessLevel,
    hasExtendedAccess,
    hasLimitedAccess,
    hasPublicAccess,
    setUserAccessLevel
  }
})
