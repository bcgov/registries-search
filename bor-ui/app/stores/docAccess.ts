/** Manages business search document access data */
export const useDocAccessStore = defineStore('docAccess', () => {
  const docAccessHistory: Ref<DocAccess[]> = ref([])
  const docAccessErrors: Ref<SearchError[]> = ref([])
  const docAccessLoading = ref(false)

  const clearDocAccessHistory = () => {
    docAccessErrors.value = []
    docAccessHistory.value = []
  }

  const loadDocAccessHistory = async () => {
    docAccessLoading.value = true
    clearDocAccessHistory()
    const respData = await useBusinessSearchApi().getDocAccessHistory()
    if (respData.error) {
      docAccessErrors.value.push(respData.error)
    } else {
      docAccessHistory.value = respData.documentAccessRequests || []
    }
    docAccessLoading.value = false
  }

  return {
    docAccessHistory,
    docAccessErrors,
    docAccessLoading,
    clearDocAccessHistory,
    loadDocAccessHistory
  }
})
