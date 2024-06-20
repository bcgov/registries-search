import { StatusCodes } from 'http-status-codes'
import type { BusinessTypeE } from '#imports'

const _getSearchBusFilters = (filters: Partial<RegSearchFilterI>) => {
  const filterParams = { query: '', categories: '' }
  // filters
  if (filters?.bn) {
    filterParams.query += `::bn:${filters.bn}`
  }
  if (filters?.identifier) {
    filterParams.query += `::identifier:${filters.identifier}`
  }
  if (filters?.name) {
    filterParams.query += `::name:${filters.name}`
  }
  // categories
  if (filters?.legalType) {
    // group specific corp types together
    if (filters.legalType === 'Other' as BusinessTypeE) {
      // query by all 'other' corp types
      filters.legalType = OtherCorpTypes.join(',') as BusinessTypeE
    } else {
      const corpGrps = [BCLimitedTypes, ULCTypes, SocietyTypes]
      for (const i in corpGrps) {
        if (corpGrps[i].includes(filters.legalType as BusinessTypeE)) {
          // query by all society corp types
          filters.legalType = corpGrps[i].join(',') as BusinessTypeE
          break
        }
      }
    }
    filterParams.categories += `legalType:${filters.legalType}`
  }
  if (filters?.status) {
    filterParams.categories += filters?.legalType ? '::' : ''
    filterParams.categories += `status:${filters.status}`
  }
  return filterParams
}

export const useRegSearchApi = () => {
  const { regSearchApiURL, regSearchApiKey } = useRuntimeConfig().public

  const searchBusiness = async (
    searchValue: string,
    filters: Partial<RegSearchFilterI>,
    rows: number,
    start: number
  ): Promise<RegSearchResponseI> => {
    if (!searchValue) { return }

    const filterParams = _getSearchBusFilters(filters)
    const params = {
      query: `value:${searchValue}${filterParams.query || ''}`,
      categories: filterParams.categories || undefined,
      start: start * rows,
      rows
    }
    // add search-api config stuff
    const config = getApiConfig(regSearchApiURL, regSearchApiKey, false, params)

    return await useBcrosFetch<RegSearchResponseI>('businesses/search/facets', config)
      .then(({ data, error }) => {
        if (error.value || !data.value) {
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

  return {
    searchBusiness
  }
}
