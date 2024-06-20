import { StatusCodes } from 'http-status-codes'
// internal
import { ErrorCategoryE, SearchAccessE } from '#imports'
import type {
  SearchAccessE as SearchAccessType,
  SearchResponseI
} from '#imports'

export const useBorSearchApi = () => {
  const { borApiURL, borApiKey } = useRuntimeConfig().public

  const searchEntities = async (
    searchValue: string,
    filters: SearchPayloadI,
    rows: number,
    start: number,
    exportSearch = false,
    accessLevel: SearchAccessType
  ): Promise<SearchResponseI | undefined> => {
    if (!searchValue) { return }
    // set payload
    const payload: SearchPayloadI = {
      ...filters,
      rows,
      start: start * rows
    }
    payload.query.value = searchValue
    // add search-api config stuff
    const config = getApiConfig(borApiURL, borApiKey, exportSearch)
    let accessPath = null
    switch (accessLevel) {
      case SearchAccessE.PUBLIC:
        accessPath = '/public'
        break
      case SearchAccessE.LIMITED:
        accessPath = ''
        break
      case SearchAccessE.EXTENDED:
        accessPath = '/extended'
        break
      default:
        console.error('Invalid access level specified: ', accessLevel)
        return
    }
    return await useBcrosFetch<SearchResponseI>(
      'search' + accessPath,
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
