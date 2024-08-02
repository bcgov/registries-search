import type { DocAccessI } from '#imports'

/** Manages reg search document access data */
export const useBcrosDocAccess = defineStore('bcros/docAccess', () => {
  const docAccessHistory: Ref<DocAccessI[]> = ref([])
  const docAccessErrors: Ref<ErrorI[]> = ref([])
  const docAccessLoading = ref(false)

  const clearDocAccessHistory = () => {
    docAccessErrors.value = []
    docAccessHistory.value = []
  }

  const loadDocAccessHistory = async () => {
    docAccessLoading.value = true
    clearDocAccessHistory()
    const respData = await useRegSearchApi().getDocAccessHistory()
    if (respData.error) {
      docAccessErrors.value.push(respData.error)
    } else {
      docAccessHistory.value = respData.documentAccessRequests
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
