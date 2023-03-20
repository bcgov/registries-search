import { computed, reactive } from 'vue'
// local
import { ErrorI, SearchFilterI, SearchI, SearchPartyFilterI, SearchResponseI } from '@/interfaces'
import { searchBusiness, searchParties } from '@/requests'
import { ErrorCategories } from '@/enums'

const DEFAULT_SEARCH_ROWS = 100

// read only globals
const _readOnly = reactive({
  error: null as ErrorI,
  loading: false,
  loadingNext: false,
  start: 0,
  value: ''
})

// globals TODO: try moving to pinia
const search = reactive({
  filters: {},
  results: null,
  searchType: 'business',
  totalResults: null,
  unavailable: false,
  _error: computed(() => _readOnly.error),
  _loading: computed(() => _readOnly.loading),
  _loadingNext: computed(() => _readOnly.loadingNext),
  _start: computed(() => _readOnly.start),
  _value: computed(() => _readOnly.value)
} as SearchI)

const _searchErrorHandler = async (searchResp: SearchResponseI) => {
  // response error with info
  search.results = []
  search.totalResults = null
  _readOnly.error = searchResp.error
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
    _readOnly.loadingNext = true
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
        _readOnly.error = null
        search.unavailable = false
      } else _searchErrorHandler(searchResp)
    } else console.error('Error getting getNextSearchResults') // should never get here
    _readOnly.loadingNext = false
  }
  const getSearchResults = async (val: string) => {
    if (!val) {
      resetSearch(search.searchType)
      return
    }
    search.totalResults = null
    _readOnly.loading = true
    _readOnly.value = val
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
        _readOnly.value = searchResp.searchResults.queryInfo.query.value
        search.results = searchResp.searchResults.results
        search.totalResults = searchResp.searchResults.totalResults
        _readOnly.error = null
        search.unavailable = false
      } else _searchErrorHandler(searchResp)
    } else {
      // unhandled response error (should never get here)
      search.results = []
      search.totalResults = null
      console.error('Nothing returned from search request fn.')
    }
    _readOnly.loading = false
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
    _readOnly.error = null
    _readOnly.loading = false
    _readOnly.start = 0
    _readOnly.value = ''
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