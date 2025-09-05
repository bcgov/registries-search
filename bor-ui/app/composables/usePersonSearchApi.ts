export const usePersonSearchApi = () => {
  const { $personSearchApi } = useNuxtApp()

  const searchEntities = async (
    searchValue: string,
    payload: SearchPayload,
    exportSearch = false
  ): Promise<SearchResponse | undefined> => {
    if (!searchValue) {
      return
    }
    // set 'value'
    payload.query.value = searchValue
    // add search-api config stuff
    const config = getApiConfig(exportSearch)
    const { accessLevel } = useSearchAccessStore()
    const { searchType } = useSearchStore()
    let searchPath = null
    if (searchType === SearchType.DIRECTOR) {
      searchPath = ''
    } else if (searchType === SearchType.PERSON) {
      switch (accessLevel) {
        case SearchAccess.PUBLIC:
          searchPath = '/public'
          break
        case SearchAccess.LIMITED:
          searchPath = '/public'
          break
        case SearchAccess.EXTENDED:
          searchPath = '/extended'
          break
        default:
          console.error('Unexpected access level: ', accessLevel)
          return
      }
    } else {
      console.error('Unexpected search type for this API: ', searchType)
    }
    return await $personSearchApi<SearchResponse>(
      'search' + searchPath,
      { method: 'POST', body: payload, ...config }
    ).then((resp) => {
      if (!exportSearch) {
        return resp
      }
      // else download file
      const { pacificDate } = useDatetime()
      const downloadName = `${pacificDate(new Date(), 'yyyy-LL-dd_HH_mm_ss')}_BC_DIRECTOR_SEARCH.xlsx`
      downloadFile(resp, downloadName)
    }).catch((err) => {
      console.warn('Error fetching search', err)
      let category = ErrorCategory.SEARCH
      if (exportSearch) {
        category = ErrorCategory.SEARCH_EXPORT
      }
      return {
        facets: {},
        searchResults: {},
        error: parseGatewayError(category, err.status, err.data)
      } as SearchResponse
    })
  }

  return {
    searchEntities
  }
}
