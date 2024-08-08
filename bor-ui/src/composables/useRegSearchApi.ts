import { StatusCodes } from 'http-status-codes'
import type { BusinessTypeE, DocAccessHistoryI, RegSearchPayloadI } from '#imports'

export const useRegSearchApi = () => {
  const { regSearchApiURL, regSearchApiURLV2, regSearchApiKey } = useRuntimeConfig().public

  /** Helper function to apply groups of legal types based on the user selection. */
  const legalTypePayloadConversion = (legalTypes: BusinessTypeE[]): BusinessTypeE[] => {
    let updatedLegalTypes = []
    for (const legalType of legalTypes ?? []) {
      const legalTypeCode = getCorpCode(legalType) || legalType
      // group specific corp type codes together
      if (legalTypeCode === 'Other' as BusinessTypeE) {
        // query by all 'other' corp types
        updatedLegalTypes = updatedLegalTypes.concat(OtherCorpTypes)
      } else {
        updatedLegalTypes.push(legalTypeCode)
        const corpGrps = [BCLimitedTypes, ULCTypes, SocietyTypes]
        for (const i in corpGrps) {
          if (corpGrps[i].includes(legalTypeCode as BusinessTypeE)) {
            // rmv dup code
            updatedLegalTypes.pop()
            // query by all grp corp types)
            updatedLegalTypes = updatedLegalTypes.concat(corpGrps[i])
            break
          }
        }
      }
    }
    return updatedLegalTypes
  }

  const searchBusiness = async (
    searchValue: string,
    payload: RegSearchPayloadI
  ): Promise<RegSearchResponseI> => {
    if (!searchValue) { return }

    // set 'value'
    payload.query.value = searchValue
    // update legal types based on selection
    payload.categories.legalType = legalTypePayloadConversion(payload.categories.legalType)
    // add search-api config stuff
    const config = getApiConfig(regSearchApiURLV2, regSearchApiKey, false)
    return await useBcrosFetch<RegSearchResponseI>('search/businesses', { method: 'POST', body: payload, ...config })
      .then(({ data, error }) => {
        if (error.value) {
          console.warn('Error fetching search')
          let category = ErrorCategoryE.SEARCH
          if (error.value.status === StatusCodes.SERVICE_UNAVAILABLE) {
            category = ErrorCategoryE.SEARCH_UNAVAILABLE
          }
          return {
            searchResults: null,
            error: parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
          } as RegSearchResponseI
        }

        return data.value
      })
  }

  const getDocAccessHistory = async (): Promise<DocAccessHistoryI> => {
    // add search-api config stuff
    const config = getApiConfig(regSearchApiURL, regSearchApiKey, false)
    return await useBcrosFetch<DocAccessHistoryI>('purchases', config)
      .then(({ data, error }) => {
        if (error.value) {
          console.warn('Error fetching document access history.')
          return {
            error: parseGatewayError(
              ErrorCategoryE.DOC_ACCESS_HISTORY,
              StatusCodes.INTERNAL_SERVER_ERROR,
              error)
          } as DocAccessHistoryI
        }
        return data.value
      })
  }

  return {
    getDocAccessHistory,
    searchBusiness
  }
}
