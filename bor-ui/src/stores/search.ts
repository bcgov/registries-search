import { SearchTypeE, type FacetsResultI, type RegSearchResultI, type SearchPayloadI } from '#imports'

const DEFAULT_SEARCH_ROWS = 50

const STARTING_FILTERS = {
  query: { roles: { roleDates: {} } },
  categories: {
    entityAddresses: {},
    roles: {}
  }
}

/** Manages bcros search data */
export const useBcrosSearch = defineStore('bcros/search', () => {
  const searchType = ref(SearchTypeE.BUSINESS)
  // when searchType changes trigger search on new selection with current search input
  watch(searchType, (_, oldVal) => getSearchResults(searches[oldVal].value.val))

  const { searchRows } = useRuntimeConfig().public

  /** Return an initialized search object based on the type. */
  const _initSearch = (type: SearchTypeE) => {
    const filters = type === SearchTypeE.BUSINESS
      ? {} as Partial<RegSearchFilterI>
      : structuredClone(STARTING_FILTERS) as Partial<SearchPayloadI>

    const results = type === SearchTypeE.BUSINESS
      ? [] as RegSearchResultI[]
      : [] as SearchResultI[]

    return ref({
      error: undefined,
      exportRows: '1000',
      loading: false,
      loadingNext: false,
      filterActive: false,
      filters,
      resultFacets: undefined as FacetsResultI,
      results,
      resultsTotal: undefined,
      rows: parseInt(searchRows) || DEFAULT_SEARCH_ROWS,
      start: 0,
      val: ''
    })
  }

  const searchBusiness = _initSearch(SearchTypeE.BUSINESS)
  const searchPerson = _initSearch(SearchTypeE.PERSON)
  const searchDirector = _initSearch(SearchTypeE.DIRECTOR)

  const searches = {
    [SearchTypeE.BUSINESS]: searchBusiness,
    [SearchTypeE.PERSON]: searchPerson,
    [SearchTypeE.DIRECTOR]: searchDirector
  }

  const activeSearch = computed(() => searches[searchType.value].value)

  /** Returns true there are more results to be returned from the api. */
  const hasMoreResults = computed(() => {
    return (activeSearch.value.resultsTotal &&
      activeSearch.value.results.length < activeSearch.value.resultsTotal)
  })

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
    return findActiveInObject(activeSearch.value.filters)
  }

  /** Call the appropriate search api based on the current state and return the response. */
  const callSearch = async (exporting = false, rows = undefined) => {
    return (searchType.value === SearchTypeE.BUSINESS
      ? await useRegSearchApi()
        .searchBusiness(
          activeSearch.value.val,
          activeSearch.value.filters as RegSearchFilterI,
          activeSearch.value.rows,
          activeSearch.value.start)
      : await useBorSearchApi()
        .searchEntities(
          activeSearch.value.val,
          activeSearch.value.filters as SearchPayloadI,
          rows || activeSearch.value.rows,
          exporting ? 0 : activeSearch.value.start,
          exporting,
          useBcrosSearchAccess().accessLevel)
    )
  }

  /** Export search to file for download. */
  const exportSearch = async () => {
    const searchResp = await callSearch(true, activeSearch.value.exportRows)
    if (searchResp && searchResp.error) {
      searchErrorHandler(searchResp.error)
    }
  }

  /** Apply filter and get results set. */
  const filterSearch = async (path: string[], val: any, reset = false) => {
    if (reset) {
      activeSearch.value.filters = searchType.value === SearchTypeE.BUSINESS
        ? {}
        : structuredClone(STARTING_FILTERS)
      await getSearchResults(activeSearch.value.val, true)
      return
    }
    const increasingScope = !val
    // path will have length of 3 at most
    if (path.length === 1) {
      // i.e. search.filters['start'] = val
      activeSearch.value.filters[path[0]] = val
    } else if (path.length === 2) {
      // i.e. search.filters['query']['bn'] = val
      activeSearch.value.filters[path[0]][path[1]] = val
    } else {
      // i.e. search.filters['query']['roles']['relatedBN'] = val
      activeSearch.value.filters[path[0]][path[1]][path[2]] = val
    }

    if (activeSearch.value.val) {
      await getSearchResults(activeSearch.value.val, increasingScope)
    }
  }

  /** Get next batch of results from the api and update the results. */
  const getNextResults = async () => {
    if (!hasMoreResults.value) { return }
    activeSearch.value.loadingNext = true
    activeSearch.value.start += 1
    // search
    const searchResp = await callSearch()
    if (searchResp) {
      if (!searchResp.error) {
        // success
        activeSearch.value.results = [
          ...activeSearch.value.results,
          ...searchResp.searchResults.results
        ] as SearchResultI[] | RegSearchResultI[]
        activeSearch.value.error = undefined
      } else {
        activeSearch.value.start -= 1
        searchErrorHandler(searchResp.error)
      }
    } else { console.error('Error getting getNextSearchResults') } // should never get here
    activeSearch.value.loadingNext = false
  }

  /** Get the first batch of results from the api and set the results. */
  const getSearchResults = async (val: string, updateFacets = true) => {
    if (!val) {
      reset(searchType.value)
      return
    }
    activeSearch.value.loading = true
    activeSearch.value.start = 0
    activeSearch.value.val = val
    // special case for query/roles/value
    // @ts-ignore
    activeSearch.value.filterActive = hasActiveFilter() || !!activeSearch.value.filters?.query?.roles?.value
    const searchResp = await callSearch()
    if (searchResp) {
      if (searchResp.error) {
        searchErrorHandler(searchResp.error)
      } else {
        // success
        if (val !== activeSearch.value.val) { return } // user updated the search value after this search was triggered

        if (updateFacets) {
          activeSearch.value.resultFacets = searchResp?.facets
        }

        activeSearch.value.error = undefined
        activeSearch.value.results = searchResp.searchResults.results
        activeSearch.value.resultsTotal = searchResp.searchResults.totalResults
      }
    } else {
      // unhandled response error (should never get here)
      activeSearch.value.results = []
      activeSearch.value.resultsTotal = undefined
      console.error('Nothing returned from search request fn.')
    }
    activeSearch.value.loading = false
  }

  /** Return the count of the facet value. */
  const facetCount = (facet: string, value: string) => {
    if (activeSearch.value.resultFacets?.fields) {
      const facetItems = activeSearch.value.resultFacets?.fields[facet] as FacetI[]
      if (facetItems) {
        const facetItem = facetItems.find(facetItem => facetItem.value.toLowerCase() === value.toLowerCase())
        if (facetItem) { return facetItem.parentCount || facetItem.count }
      }
    }
    return 0
  }

  /** Return the list of facet items of the facet field. */
  const facetItems = (facet: string) => {
    if (activeSearch.value.resultFacets?.fields) {
      return activeSearch.value.resultFacets?.fields[facet] as FacetI[] || []
    }
    return []
  }

  /** Return the highlighted search value within the match */
  const highlightMatch = (match: string) => {
    if (!activeSearch.value.val) { return match }
    if (!match) { return '' }
    return match.replaceAll(activeSearch.value.val.toUpperCase(), `<b>${activeSearch.value.val.toUpperCase()}</b>`)
  }

  const searchErrorHandler = (error: ErrorI) => {
    activeSearch.value.resultsTotal = undefined
    activeSearch.value.error = error
  }

  const reset = (type: SearchTypeE) => {
    searches[type].value.val = ''
    searches[type].value.filters = type === SearchTypeE.BUSINESS ? {} : structuredClone(STARTING_FILTERS)
    searches[type].value.results = []
    searches[type].value.resultsTotal = undefined
    searches[type].value.error = undefined
    searches[type].value.loading = false
    searches[type].value.loadingNext = false
  }

  return {
    activeSearch,
    searchType,
    searchBusiness,
    searchDirector,
    searchPerson,
    hasMoreResults,
    exportSearch,
    filterSearch,
    getNextResults,
    getSearchResults,
    facetCount,
    facetItems,
    highlightMatch,
    reset,
    searchErrorHandler
  }
})
