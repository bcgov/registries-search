import _ from 'lodash'
import { searchEntities } from '@/requests'

const STARTING_FILTERS = {
  query: { roles: { roleDates: {} } },
  categories: {
    entityAddresses: {},
    entityType: [EntityTypeE.PERSON],
    roles: {}
  }
}

const DEFAULT_SEARCH_ROWS = 50

// read only globals
const _readOnly = reactive({
  error: null as ErrorI,
  isFilteringActive: false,
  loading: false,
  loadingNext: false,
  start: 0,
  value: ''
})

// globals TODO: try moving to pinia
const search = reactive({
  exportRows: 1000,
  facetsResult: {},
  filters: _.cloneDeep(STARTING_FILTERS),
  results: null,
  totalResults: null,
  _error: computed(() => _readOnly.error),
  _isFilteringActive: computed(() => _readOnly.isFilteringActive),
  _loading: computed(() => _readOnly.loading),
  _loadingNext: computed(() => _readOnly.loadingNext),
  _start: computed(() => _readOnly.start),
  _value: computed(() => _readOnly.value)
} as SearchI)

const _searchErrorHandler = (searchResp: SearchResponseI) => {
  // response error with info
  search.results = []
  search.totalResults = null
  _readOnly.error = searchResp.error
}

export const useSearch = () => {
  /** The amount of results to return in each search batch. */
  const config = useRuntimeConfig().public
  const rows = parseInt(config.searchRows) || DEFAULT_SEARCH_ROWS

  /** Returns true if any filter has a value. */
  const hasActiveFilter = () => {
    const findActiveInObject = (object: object) => {
      for (const i in object) {
        // skip entity type filter
        if (['entityType', 'value'].includes(i)) { continue }

        if (['string', 'array'].includes(typeof (object[i]))) {
          if (object[i]) { return true }
        } else if (findActiveInObject(object[i])) { return true }
      }
      return false
    }
    return findActiveInObject(search.filters)
  }

  /** Returns true there are more results to be returned from the api. */
  const hasMoreResults = computed(() => {
    return search.totalResults && search.results?.length < search.totalResults
  })

  /** Return the count of the facet value. */
  const facetCount = (facet: string, value: string) => {
    if (search.facetsResult.fields) {
      const facetItems = search.facetsResult.fields[facet] as FacetI[]
      if (facetItems) {
        const facetItem = facetItems.find(facetItem => facetItem.value.toLowerCase() === value.toLowerCase())
        if (facetItem) { return facetItem.parentCount || facetItem.count }
      }
    }
    return 0
  }

  /** Return the list of facet items of the facet field. */
  const facetItems = (facet: string) => {
    if (search.facetsResult.fields) {
      return search.facetsResult.fields[facet] as FacetI[] || []
    }
    return []
  }

  /** Export search to file for download. */
  const exportSearch = async () => {
    const searchResp = await searchEntities(search._value, search.filters, search.exportRows, 0, true)
    if (searchResp && searchResp.error) {
      _searchErrorHandler(searchResp)
    }
  }

  /** Apply filter and get results set. */
  const filterSearch = async (path: string[], val: any, resetFilters = false) => {
    if (resetFilters) {
      search.filters = _.cloneDeep(STARTING_FILTERS)
      await getSearchResults(search._value, true)
      return
    }
    const increasingScope = !val
    // path will have length of 3 at most
    if (path.length === 1) {
      // i.e. search.filters['start'] = val
      search.filters[path[0]] = val
    } else if (path.length === 2) {
      // i.e. search.filters['query']['bn'] = val
      search.filters[path[0]][path[1]] = val
    } else {
      // i.e. search.filters['query']['roles']['relatedBN'] = val
      search.filters[path[0]][path[1]][path[2]] = val
    }

    if (search._value) { await getSearchResults(search._value, increasingScope) }
  }

  /** Get next batch of results from the api and update the results. */
  const getNextResults = async () => {
    if (!hasMoreResults.value) { return }
    _readOnly.loadingNext = true
    // search
    const searchResp = await searchEntities(search._value, search.filters, rows, search._start + 1)
    if (searchResp) {
      if (!searchResp.error) {
        // success
        _readOnly.start += 1
        search.results = [...search.results, ...searchResp.searchResults.results]
        _readOnly.error = null
      } else { _searchErrorHandler(searchResp) }
    } else { console.error('Error getting getNextSearchResults') } // should never get here
    _readOnly.loadingNext = false
  }

  /** Get the first batch of results from the api and set the results. */
  const getSearchResults = async (val: string, updateFacets = true) => {
    if (!val) {
      resetSearch()
      return
    }
    search.totalResults = null
    _readOnly.start = 0
    _readOnly.loading = true
    _readOnly.value = val
    // special case for query/roles/value
    _readOnly.isFilteringActive = hasActiveFilter() || !!search.filters?.query?.roles?.value
    if (search.results === null) { search.results = [] }
    const searchResp = await searchEntities(val, search.filters, rows, 0)
    if (searchResp) {
      if (!searchResp.error) {
        // success
        if (val !== search._value) { return } // user updated the search value after this search was triggered
        // this is the search the user is waiting on
        if (updateFacets) { search.facetsResult = searchResp.facets } else {
          // always update entityType facets since overall counts are based off them
          search.facetsResult.fields.entityType = searchResp.facets.fields.entityType
        }

        _readOnly.error = null
        search.results = searchResp.searchResults.results
        search.totalResults = searchResp.searchResults.totalResults
      } else { _searchErrorHandler(searchResp) }
    } else {
      // unhandled response error (should never get here)
      search.facetsResult = {}
      search.results = []
      search.totalResults = null
      console.error('Nothing returned from search request fn.')
    }
    _readOnly.loading = false
  }

  /** Return the highlighted search value within the match */
  const highlightMatch = (match: string) => {
    if (!search._value) { return match }
    if (!match) { return '' }
    return match.replaceAll(search._value.toUpperCase(), `<b>${search._value.toUpperCase()}</b>`)
  }

  /** Reset all search values */
  const resetSearch = () => {
    search.facetsResult = {}
    search.filters = _.cloneDeep(STARTING_FILTERS)
    search.results = null
    search.totalResults = null
    _readOnly.error = null
    _readOnly.isFilteringActive = false
    _readOnly.loading = false
    _readOnly.start = 0
    _readOnly.value = ''
  }
  return {
    search,
    hasMoreResults,
    facetCount,
    facetItems,
    exportSearch,
    filterSearch,
    getNextResults,
    getSearchResults,
    highlightMatch,
    resetSearch
  }
}
