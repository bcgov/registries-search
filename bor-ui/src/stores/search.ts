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

/** Manages bcros search data */
export const useBcrosSearch = defineStore('bcros/search', () => {
  const searchError: Ref<ErrorI> = ref(null)
  // states
  const loading = ref(false)
  const loadingNext = ref(false)
  const isFilteringActive = ref(false)
  const isExtended = ref(false)
  // search values
  const searchValue = ref('')
  const start = ref(0)
  const exportRows = ref(1000)
  const filters: Ref<SearchPayloadI> = ref(_.cloneDeep(STARTING_FILTERS))
  // search results
  const facetsResult: Ref<FacetsResultI> = ref({})
  const results: Ref<SearchResultI[]> = ref(null)
  const totalResults: Ref<number> = ref(null)

  const _searchErrorHandler = (searchResp: SearchResponseI) => {
    results.value = []
    totalResults.value = null
    searchError.value = searchResp.error
  }

  const config = useRuntimeConfig().public
  /** The amount of results to return in each search batch. */
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
    return findActiveInObject(filters.value)
  }

  /** Returns true there are more results to be returned from the api. */
  const hasMoreResults = computed(() => {
    return totalResults.value && results.value?.length < totalResults.value
  })

  /** Return the count of the facet value. */
  const facetCount = (facet: string, value: string) => {
    if (facetsResult.value.fields) {
      const facetItems = facetsResult.value.fields[facet] as FacetI[]
      if (facetItems) {
        const facetItem = facetItems.find(facetItem => facetItem.value.toLowerCase() === value.toLowerCase())
        if (facetItem) { return facetItem.parentCount || facetItem.count }
      }
    }
    return 0
  }

  /** Return the list of facet items of the facet field. */
  const facetItems = (facet: string) => {
    if (facetsResult.value.fields) {
      return facetsResult.value.fields[facet] as FacetI[] || []
    }
    return []
  }

  /** Export search to file for download. */
  const exportSearch = async () => {
    const searchResp = await searchEntities(
      searchValue.value, filters.value, exportRows.value, 0, true, isExtended.value)
    if (searchResp && searchResp.error) {
      _searchErrorHandler(searchResp)
    }
  }

  /** Apply filter and get results set. */
  const filterSearch = async (path: string[], val: any, resetFilters = false) => {
    if (resetFilters) {
      filters.value = _.cloneDeep(STARTING_FILTERS)
      await getSearchResults(searchValue.value, true)
      return
    }
    const increasingScope = !val
    // path will have length of 3 at most
    if (path.length === 1) {
      // i.e. search.filters['start'] = val
      filters.value[path[0]] = val
    } else if (path.length === 2) {
      // i.e. search.filters['query']['bn'] = val
      filters.value[path[0]][path[1]] = val
    } else {
      // i.e. search.filters['query']['roles']['relatedBN'] = val
      filters.value[path[0]][path[1]][path[2]] = val
    }

    if (searchValue.value) { await getSearchResults(searchValue.value, increasingScope) }
  }

  /** Get next batch of results from the api and update the results. */
  const getNextResults = async () => {
    if (!hasMoreResults.value) { return }
    loadingNext.value = true
    // search
    const searchResp = await searchEntities(
      searchValue.value, filters.value, rows, start.value + 1, false, isExtended.value)
    if (searchResp) {
      if (!searchResp.error) {
        // success
        start.value += 1
        results.value = [...results.value, ...searchResp.searchResults.results]
        searchError.value = null
      } else { _searchErrorHandler(searchResp) }
    } else { console.error('Error getting getNextSearchResults') } // should never get here
    loadingNext.value = false
  }

  /** Get the first batch of results from the api and set the results. */
  const getSearchResults = async (val: string, updateFacets = true) => {
    if (!val) {
      resetSearch()
      return
    }
    totalResults.value = null
    start.value = 0
    loading.value = true
    searchValue.value = val
    // special case for query/roles/value
    isFilteringActive.value = hasActiveFilter() || !!filters.value?.query?.roles?.value
    if (results.value === null) { results.value = [] }
    const searchResp = await searchEntities(val, filters.value, rows, 0, false, isExtended.value)
    if (searchResp) {
      if (searchResp.error) {
        _searchErrorHandler(searchResp)
      } else {
        // success
        if (val !== searchValue.value) { return } // user updated the search value after this search was triggered
        // this is the search the user is waiting on
        if (updateFacets) {
          facetsResult.value = searchResp.facets
        } else {
          // always update entityType facets since overall counts are based off them
          facetsResult.value.fields.entityType = searchResp.facets.fields.entityType
        }

        searchError.value = null
        results.value = searchResp.searchResults.results
        totalResults.value = searchResp.searchResults.totalResults
      }
    } else {
      // unhandled response error (should never get here)
      facetsResult.value = {}
      results.value = []
      totalResults.value = null
      console.error('Nothing returned from search request fn.')
    }
    loading.value = false
  }

  /** Return the highlighted search value within the match */
  const highlightMatch = (match: string) => {
    if (!searchValue.value) { return match }
    if (!match) { return '' }
    return match.replaceAll(searchValue.value.toUpperCase(), `<b>${searchValue.value.toUpperCase()}</b>`)
  }

  const resetSearch = () => {
    facetsResult.value = {}
    filters.value = _.cloneDeep(STARTING_FILTERS)
    results.value = null
    totalResults.value = null
    searchError.value = null
    isFilteringActive.value = false
    loading.value = false
    start.value = 0
    searchValue.value = ''
  }

  return {
    searchError,
    loading,
    loadingNext,
    isExtended,
    isFilteringActive,
    searchValue,
    start,
    exportRows,
    filters,
    facetsResult,
    results,
    totalResults,
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
})
