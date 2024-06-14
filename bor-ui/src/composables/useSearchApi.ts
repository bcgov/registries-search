import { StatusCodes } from 'http-status-codes'
// internal
import { ErrorCategoryE, SearchAccessE } from '#imports'
import type {
  ErrorCategoryE as ErrCategoryType,
  ErrorCodeE,
  SearchAccessE as SearchAccessType,
  SearchResponseI
} from '#imports'

export const useSearchApi = () => {
  const _getSearchConfig = (exportSearch: boolean) => {
    const { borApiURL, borApiKey } = useRuntimeConfig().public
    if (!borApiURL) { console.error('Error: BOR_API_URL expected, but not found.') }
    if (!borApiKey) { console.error('Error: BOR_API_KEY expected, but not found.') }

    const config: any = { baseURL: borApiURL, headers: { 'x-apikey': borApiKey } }
    if (exportSearch) {
      config.headers.Accept = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      config.responseType = 'blob'
    }
    return config
  }

  const _parseGatewayError = (category: ErrCategoryType, defaultStatus: StatusCodes, error): ErrorI => {
    const parseRootCause = (rootCause: string) => {
      try {
        let parsedRootCause = rootCause.replace('detail:', '"detail":"')
          .replace('type:', '"type":"')
          .replace('message:', '"message":"')
          .replace('status_code:', '"statusCode":"')
          .replaceAll(',', '",')
        parsedRootCause = `{${parsedRootCause}"}`
        return JSON.parse(parsedRootCause)
      } catch (error) {
        console.warn(error)
        return null
      }
    }
    // parse root cause
    let rootCause = null
    if (error.value?.data?.rootCause) { rootCause = parseRootCause(error.value.data.rootCause) }
    return {
      category,
      detail: rootCause?.detail || error?.response?.data?.detail,
      message: rootCause?.message || error?.response?.data?.message,
      statusCode: rootCause?.statusCode || error?.response?.status || defaultStatus,
      type: rootCause?.type?.trim() as ErrorCodeE
    }
  }

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
    const config = _getSearchConfig(exportSearch)
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
            error: _parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
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
