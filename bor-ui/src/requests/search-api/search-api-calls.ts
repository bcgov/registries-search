import Axios from 'axios'
import { StatusCodes } from 'http-status-codes'
import { getSearchConfig, parseGatewayError } from './search-api-utils'
import { addAxiosInterceptors } from '@/utils/axios'
// internal

const axios = addAxiosInterceptors(Axios.create())
// eslint-disable-next-line
export async function searchEntities (
  searchValue: string,
  filters: SearchPayloadI,
  rows: number,
  start: number,
  exportSearch = false,
  extended = false
): Promise<SearchResponseI | undefined> {
  if (!searchValue) { return }
  // set payload
  const payload: SearchPayloadI = {
    ...filters,
    rows,
    start: start * rows
  }
  payload.query.value = searchValue
  // add search-api config stuff
  const config = getSearchConfig(exportSearch)
  return axios.post<SearchResponseI>(`search${extended ? '/extended' : ''}`, payload, config)
    .then((response) => {
      const data: SearchResponseI = response?.data
      if (!data) { throw new Error('Invalid API response') }

      if (!exportSearch) { return data }

      const { pacificDate } = useDatetime()
      const downloadName = `${pacificDate(new Date(), 'YYYY-MM-DD_HH_mm_ss')}_BC_DIRECTOR_SEARCH.xlsx`
      downloadFile(response.data as any, downloadName)
    }).catch((error) => {
      let category = ErrorCategoryE.SEARCH
      if (exportSearch) { category = ErrorCategoryE.SEARCH_EXPORT }
      return {
        facets: null,
        searchResults: null,
        error: parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
      }
    })
}
