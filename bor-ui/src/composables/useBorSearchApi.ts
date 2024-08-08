import { StatusCodes } from 'http-status-codes'
// internal
import { ErrorCategoryE, SearchAccessE } from '#imports'
import type { SearchResponseI } from '#imports'

export const useBorSearchApi = () => {
  const { borApiURL, borApiKey } = useRuntimeConfig().public

  const searchEntities = async (
    searchValue: string,
    payload: SearchPayloadI,
    exportSearch = false
  ): Promise<SearchResponseI> => {
    if (!searchValue) { return }
    // set 'value'
    payload.query.value = searchValue
    // add search-api config stuff
    const config = getApiConfig(borApiURL, borApiKey, exportSearch)
    const { accessLevel } = useBcrosSearchAccess()
    const { searchType } = useBcrosSearch()
    let searchPath = null
    if (searchType === SearchTypeE.DIRECTOR) {
      searchPath = ''
    } else if (searchType === SearchTypeE.PERSON) {
      switch (accessLevel) {
        case SearchAccessE.PUBLIC:
          searchPath = '/public'
          break
        case SearchAccessE.LIMITED:
          searchPath = '/public'
          break
        case SearchAccessE.EXTENDED:
          searchPath = '/extended'
          break
        default:
          console.error('Unexpected access level: ', accessLevel)
          return
      }
    } else {
      console.error('Unexpected search type for this API: ', searchType)
    }
    return await useBcrosFetch<SearchResponseI>(
      'search' + searchPath,
      { method: 'POST', body: payload, ...config }
    )
      .then(({ data, error }) => {
        if (error.value || !data.value) {
          console.warn('Error fetching search')
          let category = ErrorCategoryE.SEARCH
          if (exportSearch) { category = ErrorCategoryE.SEARCH_EXPORT }
          return {
            facets: {},
            searchResults: {},
            error: parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
          } as SearchResponseI
        }

        if (!exportSearch) { return data.value }
        // else download file
        const { pacificDate } = useDatetime()
        const downloadName = `${pacificDate(new Date(), 'YYYY-MM-DD_HH_mm_ss')}_BC_DIRECTOR_SEARCH.xlsx`
        downloadFile(data as any, downloadName)
      })
  }

  return {
    searchEntities
  }
}
