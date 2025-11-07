/** Manages business search document access data */
export const useDocAccessStore = defineStore('docAccess', () => {
  const { getDocAccessById, submitAccessRequest } = useBusinessSearchApi()
  const localePath = useLocalePath()
  const docAccessHistory = ref<DocAccess[]>([])
  const docAccessErrors = ref<SearchError[]>([])
  const docAccessLoading = ref(false)
  const docAccess = shallowRef<DocAccess | undefined>(undefined)

  const clearDocAccessHistory = () => {
    docAccessErrors.value = []
    docAccessHistory.value = []
  }

  const loadDocAccessHistory = async () => {
    clearDocAccessHistory()
    const respData = await useBusinessSearchApi().getDocAccessHistory()
    if (respData.error) {
      docAccessErrors.value.push(respData.error)
    } else {
      docAccessHistory.value = respData.documentAccessRequests || []
    }
  }

  const openDocAccessErrorModal = (i18nPrefix: string, redirect = false) => {
    const buttons = [
      { label: 'OK',
        shouldClose: true,
        ...(redirect
          ? { onClick: () => { useRouter().push(localePath('/')) } }
          : {})
      }]
    useModal().errorModal.open({
      error: { statusCode: 500 },
      i18nPrefix,
      buttons,
      showHelpContact: true
    })
  }

  const loadDocAccess = async (darId: number) => {
    if (docAccess.value?.id !== darId) {
      const response = await getDocAccessById(String(darId))
      if (!response.error) {
        docAccess.value = response
      } else {
        docAccessErrors.value.push(response.error)
      }
    }
    const respData = await useBusinessSearchApi().getDocAccessHistory()
    if (respData.error) {
      docAccessErrors.value.push(respData.error)
      openDocAccessErrorModal('errorModal.loadDocAccess')
    } else {
      docAccessHistory.value = respData.documentAccessRequests || []
    }
  }

  const submitDocAccess = async (businessIdentifier: string, businessName: string) => {
    const { fees } = useConnectFeeStore()
    if (fees && Object.keys(fees).length) {
      const selectedDocTypes = Object.keys(fees).map((fee) => {
        switch (fee) {
          case SearchFeeCode.BSRCH:
          case SearchFeeCode.SBSRCH:
            return DocAccessType.BUSINESS_SUMMARY_FILING_HISTORY
          case SearchFeeCode.CGOOD:
            return DocAccessType.CERTIFICATE_OF_GOOD_STANDING
          case SearchFeeCode.CSTAT:
            return DocAccessType.CERTIFICATE_OF_STATUS
          case SearchFeeCode.LSEAL:
            return DocAccessType.LETTER_UNDER_SEAL
        }
      }).filter(val => !!val)

      if (selectedDocTypes?.length) {
        const docAccessResp = await submitAccessRequest(
          businessIdentifier,
          businessName,
          selectedDocTypes,
          useStaffPaymentStore().staffPayment
        )
        if (!docAccessResp || docAccessResp?.error) {
          openDocAccessErrorModal('errorModal.submitAccessRequest')
        }
        else if (
          docAccessResp.status === DocAccessStatus.CREATED
          && docAccessResp.paymentToken
          && !docAccessResp.paymentCompletionDate
        ) {
          const path = localePath('') + `/${docAccessResp.id}`
          const url = new URL(path, useRuntimeConfig().public.baseUrl)
          const encodedURI = encodeURIComponent(url.href)
          const paymentUrl = useRuntimeConfig().public.authWebUrl + 'makepayment'
          const directPayUrl = `${paymentUrl}/${docAccessResp.paymentToken}/${encodedURI}`

          window.location.assign(directPayUrl)
        } else {
          docAccess.value = docAccessResp
          useRouter().push(localePath(`/open/${docAccessResp.businessIdentifier}/${docAccessResp.id}`))
        }
      } else {
        console.error('No valid fee codes selected for doc access attempt.')
        openDocAccessErrorModal('errorModal.submitAccessRequest')
      }
    }
  }

  const init = async (darId?: string) => {
    docAccessLoading.value = true
    const promises = [
      loadDocAccessHistory(),
      ...(darId ? [loadDocAccess(Number(darId))] : [])
    ]
    await Promise.all(promises)
    docAccessLoading.value = false
  }

  const $reset = () => {
    docAccess.value = undefined
    docAccessHistory.value = []
    docAccessLoading.value = false
    docAccessErrors.value = []
  }

  return {
    docAccess,
    docAccessHistory,
    docAccessErrors,
    docAccessLoading,
    init,
    submitDocAccess,
    $reset
  }
})
