import Axios from 'axios'
import { StatusCodes } from 'http-status-codes'
// internal
import { getSearchConfig, parseGatewayError } from './search-api-utils'
import { addAxiosInterceptors } from '@/utils/axios'
import { SearchAccessE } from '#imports'
import type { SearchAccessE as SearchAccessType, SearchResponseI } from '#imports'

const axios = addAxiosInterceptors(Axios.create())
// eslint-disable-next-line
export async function searchEntities (
  searchValue: string,
  filters: SearchPayloadI,
  rows: number,
  start: number,
  exportSearch = false,
  accessLevel: SearchAccessType
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
  return axios.post<SearchResponseI>('search' + accessPath, payload, config)
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
        facets: {},
        searchResults: {},
        error: parseGatewayError(category, StatusCodes.INTERNAL_SERVER_ERROR, error)
      } as SearchResponseI
    })
}
