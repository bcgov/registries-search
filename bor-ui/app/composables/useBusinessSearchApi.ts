import { StatusCodes } from 'http-status-codes'

export const useBusinessSearchApi = () => {
  const { $businessSearchApi } = useNuxtApp()

  /** Helper function to apply groups of legal types based on the user selection. */
  const legalTypePayloadConversion = (legalTypes: BusinessType[] | undefined): BusinessType[] => {
    let updatedLegalTypes: BusinessType[] = []
    for (const legalType of legalTypes ?? []) {
      const legalTypeCode = getCorpCode(legalType) || legalType
      // group specific corp type codes together
      if (legalTypeCode === 'Other' as BusinessType) {
        // query by all 'other' corp types
        updatedLegalTypes = updatedLegalTypes.concat(OtherCorpTypes)
      } else {
        updatedLegalTypes.push(legalTypeCode)
        const corpGrps = [BCLimitedTypes, ULCTypes, SocietyTypes]
        for (const corpGrp of corpGrps) {
          if (corpGrp.includes(legalTypeCode as BusinessType)) {
            // rmv dup code
            updatedLegalTypes.pop()
            // query by all grp corp types)
            updatedLegalTypes = updatedLegalTypes.concat(corpGrp)
            break
          }
        }
      }
    }
    return updatedLegalTypes
  }

  const searchBusiness = async (
    searchValue: string,
    payload: BusinessSearchPayload
  ): Promise<BusinessSearchResponse | undefined> => {
    if (!searchValue) {
      return
    }

    // set 'value'
    payload.query.value = searchValue
    // update legal types based on selection
    payload.categories.legalType = legalTypePayloadConversion(payload.categories.legalType)
    return await $businessSearchApi<BusinessSearchResponse>(
      'search/businesses',
      { method: 'POST', body: payload }
    ).catch(({ data, status }) => {
      console.warn('Error fetching search')
      let category = ErrorCategory.SEARCH
      if (status === StatusCodes.SERVICE_UNAVAILABLE) {
        category = ErrorCategory.SEARCH_UNAVAILABLE
      }
      return {
        searchResults: {},
        error: parseGatewayError(category, status, data)
      } as BusinessSearchResponse
    })
  }

  const getDocAccessById = async (darId: string): Promise<DocAccess> => {
    // add search-api config stuff
    const config = getApiConfig(false, undefined)
    return await $businessSearchApi<{ documentAccessRequest: DocAccess }>(`purchases/${darId}`, config)
      .then(response => response.documentAccessRequest)
      .catch(({ data, status }) => {
        console.warn('Error fetching document access request.')
        return {
          error: parseGatewayError(
            ErrorCategory.DOC_ACCESS_REQUEST,
            status,
            data)
        } as DocAccess
      })
  }

  const getDocAccessDocument = async (
    businessId: string,
    documentKey: string,
    filingId?: number | string
  ): Promise<Blob | { error: SearchError }> => {
    const config = {
      headers: { Accept: 'application/pdf' },
      responseType: 'blob' as 'json'
    }
    return await $businessSearchApi<Blob | { error: SearchError }>(
      filingId
        ? `businesses/${businessId}/documents/filings/${filingId}/${documentKey}`
        : `businesses/${businessId}/documents/${documentKey}`,
      config
    )
      .catch(({ data, status }) => {
        console.warn('Error fetching document access request document pdf.')
        return {
          error: parseGatewayError(
            ErrorCategory.DOC_ACCESS_DOWNLOAD,
            status,
            data)
        }
      })
  }

  const getDocAccessHistory = async (): Promise<DocAccessHistory> => {
    // add search-api config stuff
    const config = getApiConfig(false, undefined)
    return await $businessSearchApi<DocAccessHistory>('purchases', config)
      .catch(({ data, status }) => {
        console.warn('Error fetching document access history.')
        return {
          error: parseGatewayError(
            ErrorCategory.DOC_ACCESS_HISTORY,
            status,
            data)
        } as DocAccessHistory
      })
  }

  /**
   * Fetches the list of documents belonging to a particular filing
   *
   * @param businessId  - The business identifier
   * @param filingId - filing Id
   * @returns List of documents applicable for the specified filing
   */
  const getDocumentList = async (
    businessId: string,
    filingId: string | number
  ): Promise<BusinessFilingDocumentUrls> => {
    const resp = await $businessSearchApi<{ documents: BusinessFilingDocumentUrls }>(
      `businesses/${businessId}/documents/filings/${filingId}`)
    return resp.documents
  }

  const submitAccessRequest = async (
    business_identifier: string,
    business_name: string,
    documentList: DocAccessType[],
    staffPayInfo: StaffPayment
  ): Promise<DocAccess | undefined> => {
    const staffPayHeader = {
      ...staffPayInfo,
      waiveFees: staffPayInfo.option === StaffPaymentOption.NO_FEE
    }

    const payload: DocAccessSubmission = {
      header: staffPayHeader,
      business: {
        businessName: business_name
      },
      documentAccessRequest: {
        documents: documentList.map(doc => ({ type: doc }))
      }
    }
    return await $businessSearchApi<DocAccess>(
      `businesses/${business_identifier}/documents/requests`,
      { method: 'POST', body: payload }
    )
      .catch(({ data, status }) => {
        console.warn('Error submitting document access.')
        parseGatewayError(ErrorCategory.DOC_ACCESS_CREATE, status, data)
        return {
          error: parseGatewayError(
            ErrorCategory.DOC_ACCESS_CREATE,
            status,
            data)
        } as DocAccess
      })
  }

  return {
    getDocAccessById,
    getDocAccessDocument,
    getDocAccessHistory,
    getDocumentList,
    searchBusiness,
    submitAccessRequest
  }
}
