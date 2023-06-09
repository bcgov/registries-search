import { computed, reactive } from 'vue'
import _ from 'lodash'
// local
import { ErrorI, FacetI, SearchI, SearchResponseI } from '@/interfaces'
import { searchEntities } from '@/requests'
import { EntityType, ErrorCategory } from '@/enums'

const STARTING_FILTERS = {
  query: { roles: { roleDates: {} }},
  categories: {
    entityAddresses: {},
    entityType: [EntityType.PERSON],
    roles:{}
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
  facetsResult: {},
  filters: _.cloneDeep(STARTING_FILTERS),
  results: null,
  totalResults: null,
  unavailable: false,
  _error: computed(() => _readOnly.error),
  _isFilteringActive: computed(() => _readOnly.isFilteringActive),
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
  if (searchResp.error.category === ErrorCategory.SEARCH_UNAVAILABLE) {
    search.unavailable = true
  } else search.unavailable = false
}

export const useSearch = () => {
  /** The amount of results to return in each search batch. */
  const rows = parseInt(sessionStorage.getItem('SEARCH_ROWS')) || DEFAULT_SEARCH_ROWS

  /** Returns true if any filter has a value. */
  const hasActiveFilter = () => {
    const findActiveInObject = (object: object) => {
      for (const i in object) {
        // skip entity type filter
        if (['entityType', 'value'].includes(i)) continue

        if (['string','array'].includes(typeof(object[i]))) {
          if (object[i]) return true
        } else {
          if (findActiveInObject(object[i])) return true
        }
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
        const facetItem = facetItems.find((facetItem) => facetItem.value.toLowerCase() === value.toLowerCase())
        if (facetItem) return facetItem.parentCount || facetItem.count
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

  /** Apply filter and get results set. */
  const filterSearch = async (path: string[], val: any, resetFilters = false) => {
    if (resetFilters) {
      search.filters = _.cloneDeep(STARTING_FILTERS)
      await getSearchResults(search._value, true)
      return
    }
    const increasing_scope = !val
    // path will have length of 3 at most
    // i.e. search.filters['start'] = val
    if (path.length === 1) {
      search.filters[path[0]] = val
    }
    // i.e. search.filters['query']['bn'] = val
    else if (path.length === 2) {
      search.filters[path[0]][path[1]] = val
    }
    // i.e. search.filters['query']['roles']['relatedBN'] = val
    else search.filters[path[0]][path[1]][path[2]] = val

    if (search._value) await getSearchResults(search._value, increasing_scope)
  }

  /** Get next batch of results from the api and update the results. */
  const getNextResults = async () => {
    if (!hasMoreResults.value) return
    _readOnly.loadingNext = true
    // search
    const searchResp = await searchEntities(search._value, search.filters, rows, search._start + 1)
    if (searchResp) {
      if (!searchResp.error) {
        // success
        _readOnly.start += 1
        search.results = [...search.results, ...searchResp.searchResults.results]
        _readOnly.error = null
        search.unavailable = false
      } else _searchErrorHandler(searchResp)
    } else console.error('Error getting getNextSearchResults') // should never get here
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
    _readOnly.isFilteringActive = hasActiveFilter()
    if (search.results === null && !search.unavailable) search.results = []
    const searchResp = await searchEntities(val, search.filters, rows, 0)
    if (searchResp) {
      if (!searchResp.error) {
        // success
        if (updateFacets) search.facetsResult = searchResp.facets
        else {
          // always update entityType facets since overall counts are based off them
          search.facetsResult.fields.entityType = searchResp.facets.fields.entityType
        }

        _readOnly.value = searchResp.searchResults.queryInfo.query.value
        _readOnly.error = null
        search.results = searchResp.searchResults.results
        search.totalResults = searchResp.searchResults.totalResults
        search.unavailable = false

      } else _searchErrorHandler(searchResp)
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
    if (!search._value) return match
    if (!match) return ''
    return match.replaceAll(search._value.toUpperCase(), `<b>${search._value.toUpperCase()}</b>`)
  }

  /** Reset all search values */
  const resetSearch = () => {
    search.facetsResult = {}
    search.filters = _.cloneDeep(STARTING_FILTERS)
    search.results = null
    search.totalResults = null
    search.unavailable = false
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
    filterSearch,
    getNextResults,
    getSearchResults,
    highlightMatch,
    resetSearch
  }
}