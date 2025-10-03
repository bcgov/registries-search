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

  return {
    getDocAccessHistory,
    searchBusiness
  }
}
