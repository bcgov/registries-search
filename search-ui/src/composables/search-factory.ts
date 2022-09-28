import { computed, reactive } from 'vue'
// local
import { SearchFilterI, SearchI, SearchPartyFilterI, SearchResponseI } from '@/interfaces'
import { searchBusiness, searchParties } from '@/requests'
import { ErrorCategories } from '@/enums'

const DEFAULT_SEARCH_ROWS = 100

const search = reactive({
  filters: {},
  results: null,
  searchType: 'business',
  totalResults: null,
  unavailable: false,
  _error: null,
  _loading: false,
  _loadingNext: false,
  _start: 0,
  _value: '',
} as SearchI)

const _searchErrorHandler = async (searchResp: SearchResponseI) => {
  // response error with info
  search.results = []
  search.totalResults = null
  search._error = searchResp.error
  if (searchResp.error.category === ErrorCategories.SEARCH_UNAVAILABLE) {
    search.unavailable = true
  } else search.unavailable = false
}

export const useSearch = () => {
  const filtering = computed(() => {
    for (const i in search.filters) if (search.filters[i] !== '') return true
    return false
  })
  const hasMoreResults = computed(() => {
    return search.totalResults && search.results?.length < search.totalResults
  })
  const filterSearch = async (filterField: string, val: string) => {
    // FUTURE: verify filterField is valid
    search.filters[filterField] = val
    if (search._value) await getSearchResults(search._value)
  }
  const getNextResults = async () => {
    if (!hasMoreResults.value) return
    search._loadingNext = true
    let searchResp: SearchResponseI = null
    // FUTURE: add SEARCH_ROWS to enum
    const rows = parseInt(sessionStorage.getItem('SEARCH_ROWS')) || DEFAULT_SEARCH_ROWS
    if (search.searchType === 'business') {
      // business search
      searchResp = await searchBusiness(search._value, search.filters as SearchFilterI, rows, search._start + 1)
    } else {
      // owner search
      searchResp = await searchParties(search._value, search.filters as SearchPartyFilterI, rows, search._start + 1)
    }
    if (searchResp) {
      if (!searchResp.error) {
        // success
        search._start += 1
        search.results = [...search.results, ...searchResp.searchResults.results]
        search._error = null
        search.unavailable = false
      } else _searchErrorHandler(searchResp)
    } else console.error('Error getting getNextSearchResults') // should never get here
    search._loadingNext = false
  }
  const getSearchResults = async (val: string) => {
    if (!val) {
      resetSearch(search.searchType)
      return
    }
    search._loading = true
    search.totalResults = null
    search._value = val
    if (search.results === null && !search.unavailable) search.results = []
    let searchResp: SearchResponseI = null
    // FUTURE: add SEARCH_ROWS to enum
    const rows = parseInt(sessionStorage.getItem('SEARCH_ROWS')) || DEFAULT_SEARCH_ROWS
    if (search.searchType === 'business') {
      // business search
      searchResp = await searchBusiness(val, search.filters as SearchFilterI, rows, 0)
    } else {
      // owner search
      searchResp = await searchParties(val, search.filters as SearchPartyFilterI, rows, 0)
    }
    if (searchResp) {
      if (!searchResp.error) {
        // success
        search._value = searchResp.searchResults.queryInfo.query.value
        search.results = searchResp.searchResults.results
        search.totalResults = searchResp.searchResults.totalResults
        search._error = null
        search.unavailable = false
      } else _searchErrorHandler(searchResp)
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
  const resetSearch = (searchType: 'business' | 'partner' = 'business') => {
    search.filters = {} as SearchFilterI
    search.results = null
    search.searchType = searchType
    search.totalResults = null
    search.unavailable = false
    search._error = null
    search._loading = false
    search._start = 0
    search._value = ''
  }
  return {
    search,
    filtering,
    hasMoreResults,
    filterSearch,
    getNextResults,
    getSearchResults,
    highlightMatch,
    resetSearch
  }
}