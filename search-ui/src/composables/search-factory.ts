import { reactive } from 'vue'
// local
import { SearchFilterI, SearchI, SearchPartyFilterI, SearchResponseI } from '@/interfaces'
import { searchBusiness, searchParties } from '@/requests'
import { ErrorCategories } from '@/enums'

const search = reactive({
  filters: {},
  results: null,
  searchType: 'business',
  totalResults: null,
  unavailable: false,
  _error: null,
  _loading: false,
  _value: '',
} as SearchI)

export const useSearch = () => {
  const filterSearch = async (filterField: string, val: string) => {
    // FUTURE: verify filterField is valid
    search.filters[filterField] = val
    if (search._value) await getSearchResults(search._value)
  }
  const getSearchResults = async (val: string) => {
    search._loading = true
    if (search.results === null && !search.unavailable) search.results = []
    let searchResp: SearchResponseI = null
    if (search.searchType === 'business') {
      // business search
      searchResp = await searchBusiness(val, search.filters as SearchFilterI)
    } else {
      // owner search
      searchResp = await searchParties(val, search.filters as SearchPartyFilterI)
    }
    if (searchResp) {
      if (!searchResp.error) {
        // success
        search._value = searchResp.searchResults.queryInfo.query.value
        search.results = searchResp.searchResults.results
        search.totalResults = searchResp.searchResults.totalResults
        search._error = null
        search.unavailable = false
      } else {
        // response error with info
        search.results = null
        search.totalResults = null
        search._error = searchResp.error
        if (searchResp.error.category === ErrorCategories.SEARCH_UNAVAILABLE) {
          search.unavailable = true
        } else search.unavailable = false
      }
    } else {
      // unhandled response error (should never get here)
      search.results = []
      search.totalResults = null
      console.error('Nothing returned from search request fn.')
    }
    search._loading = false
  }
  const highlightMatch = (match: string) => {
    if (!search._value) return match
    if (!match) return ''
    return match.replaceAll(search._value.toUpperCase(), `<b>${search._value.toUpperCase()}</b>`)
  }
  const resetSearch = () => {
    search.filters = {} as SearchFilterI
    search.results = null
    search.searchType = 'business'
    search.totalResults = null
    search.unavailable = false
    search._error = null
    search._loading = false
    search._value = ''
  }
  return {
    search,
    filterSearch,
    getSearchResults,
    highlightMatch,
    resetSearch
  }
}