import { axios } from '@/utils'
import { StatusCodes } from 'http-status-codes'
// local
import { ErrorCategory } from '@/enums'
import { SearchResponseI, SearchPayloadI } from '@/interfaces'
// internal
import { getSearchConfig, parseGatewayError } from './search-api-utils'

export async function searchEntities(
  searchValue: string,
  filters: SearchPayloadI,
  rows: number,
  start: number
): Promise<SearchResponseI> {
  if (!searchValue) return
  // set payload
  const payload: SearchPayloadI = {
    ...filters,
    'rows': rows,
    'start': start * rows
  }
  payload.query.value = searchValue
  // add search-api config stuff
  const config = getSearchConfig()
  return axios.post<SearchResponseI>('search/entities', payload, config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      let category = ErrorCategory.SEARCH
      if (error?.response?.status === StatusCodes.SERVICE_UNAVAILABLE) category = ErrorCategory.SEARCH_UNAVAILABLE

      return {
        facets: null,
        searchResults: null,
        error: parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
      }
    })
}
