import { reactive } from 'vue'
// local
import { SearchI, SearchResponseI } from '@/interfaces'
import { searchBusiness, searchParties } from '@/requests'

const search = reactive({
  results: null,
  searchType: 'business',
  totalResults: null,
  _error: null,
  _loading: false,
  _value: '', // not used for anything yet
} as SearchI)

export const useSearch = () => {
  const getSearchResults = async (val: string) => {
    search._loading = true
    search._value = val
    search.results = []
    search.totalResults = null
    let searchResp: SearchResponseI = null
    if (search.searchType === 'business') searchResp = await searchBusiness(val)
    else searchResp = await searchParties(val)
    if (searchResp) {
      if (searchResp.error) {
        search.results = []
        search.totalResults = null
        search._error = searchResp.error
      } else {
        search.results = searchResp.searchResults.results
        search.totalResults = searchResp.searchResults.totalResults
      }
    } else {
      search.results = []
      search.totalResults = null
      console.error('Nothing returned from search request fn.')
    }
    search._loading = false
  }
  return {
    search,
    getSearchResults
  }
}