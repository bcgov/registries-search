import { axios } from '@/utils'
import { StatusCodes } from 'http-status-codes'
// local
import { ErrorCategories } from '@/enums'
import { SearchResponseI, SearchFilterI, SearchPartyFilterI } from '@/interfaces'
// internal
import { addSearchBusFilters, addSearchPartyFilters, getSearchConfig, parseGatewayError } from './search-api-utils'

export async function searchBusiness(
  searchValue: string,
  filters: SearchFilterI,
  rows: number,
  start: number
): Promise<SearchResponseI> {
  if (!searchValue) return
  // basic params
  const params = { query: `value:${searchValue}`, start: start * rows, rows: rows }
  // add filters
  const filterParams = addSearchBusFilters(filters)
  if (filterParams.query) params.query += filterParams.query
  if (filterParams.categories) params['categories'] = filterParams.categories
  // add search-api config stuff
  const config = getSearchConfig(params)
  return axios.get<SearchResponseI>('businesses/search/facets', config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      let category = ErrorCategories.SEARCH
      if (error?.response?.status === StatusCodes.SERVICE_UNAVAILABLE) category = ErrorCategories.SEARCH_UNAVAILABLE

      return {
        searchResults: null,
        error: parseGatewayError(category, StatusCodes.NOT_FOUND, error)
      }
    })
}

export async function searchParties(
  searchValue: string,
  filters: SearchPartyFilterI,
  rows: number,
  start: number
): Promise<SearchResponseI> {
  if (!searchValue) return

  // basic params
  const params = {
    query: `value:${searchValue}`,
    categories: 'partyRoles:partner,proprietor',
    start: start * rows,
    rows: rows
  }
  // add filters
  const filterParams = addSearchPartyFilters(filters)
  if (filterParams.query) params.query += filterParams.query
  if (filterParams.categories) params.categories = filterParams.categories
  // add search-api config stuff
  const config = getSearchConfig(params)
  return axios.get<SearchResponseI>('businesses/search/parties', config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      let category = ErrorCategories.SEARCH
      if (error?.response?.status === StatusCodes.SERVICE_UNAVAILABLE) category = ErrorCategories.SEARCH_UNAVAILABLE

      return {
        searchResults: null,
        error: parseGatewayError(category, StatusCodes.NOT_FOUND, error)
      }
    })
}
