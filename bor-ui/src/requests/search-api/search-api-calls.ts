import { axios } from '@/utils'
import { StatusCodes } from 'http-status-codes'
// local
import { SearchResponseI, SearchPayloadI } from '@/interfaces'
import { ErrorCategory } from '@/enums'
import { useDatetime } from '@/composables'
import { downloadFile } from '@/utils'
// internal
import { getSearchConfig, parseGatewayError } from './search-api-utils'

export async function searchEntities(
  searchValue: string,
  filters: SearchPayloadI,
  rows: number,
  start: number,
  exportSearch = false
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
  const config = getSearchConfig(exportSearch)
  return axios.post<SearchResponseI>('search/entities', payload, config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) throw new Error('Invalid API response')

      if (!exportSearch) return data

      const { pacificDate } = useDatetime()
      const downloadName = `${pacificDate(new Date(), 'YYYY-MM-DD_HH_mm_ss')}_BC_DIRECTOR_SEARCH.xlsx`
      downloadFile(response.data as any, downloadName)

    }).catch(error => {
      let category = ErrorCategory.SEARCH
      if (exportSearch) category = ErrorCategory.SEARCH_EXPORT
      return {
        facets: null,
        searchResults: null,
        error: parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
      }
    })
}
