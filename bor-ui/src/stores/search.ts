import mergeWith from 'lodash.mergewith'
import { SearchTypeE } from '#imports'

const DEFAULT_SEARCH_ROWS = 50

const STARTING_FILTERS: SearchPayloadI | RegSearchPayloadI = {
  query: {},
  categories: {}
}

/** Manages bcros search data */
export const useBcrosSearch = defineStore('bcros/search', () => {
  const searchType = ref(SearchTypeE.BUSINESS)
  // when searchType changes trigger search on new selection with current search input
  watch(searchType, (_, oldVal) => { getSearchResults(searches[oldVal].value.val) })

  const { searchRows } = useRuntimeConfig().public

  /** Return an initialized search object based on the type. */
  const _initSearch = (type: SearchTypeE) => {
    const filters = structuredClone(STARTING_FILTERS)

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
  const callSearch = async (exporting = false, rows?: number) => {
    rows ??= activeSearch.value.rows
    return (searchType.value === SearchTypeE.BUSINESS
      ? await useRegSearchApi()
        .searchBusiness(
          activeSearch.value.val,
          {
            ...structuredClone(toRaw(activeSearch.value.filters)),
            rows,
            start: activeSearch.value.start * rows
          } as RegSearchPayloadI
        )
      : await useBorSearchApi()
        .searchEntities(
          activeSearch.value.val,
          {
            ...structuredClone(toRaw(activeSearch.value.filters)),
            rows,
            start: exporting ? 0 : activeSearch.value.start
          } as SearchPayloadI,
          exporting
        )
    )
  }

  /** Export search to file for download. */
  const exportSearch = async () => {
    const searchResp = await callSearch(true, Number(activeSearch.value.exportRows))
    if (searchResp && searchResp.error) {
      searchErrorHandler(searchResp.error)
    }
  }

  /** Apply filter and get results set. */
  const filterSearch = async (path: string[], val: any, reset = false) => {
    const search = searches[searchType.value]
    if (reset) {
      search.value.filters = structuredClone(STARTING_FILTERS)
      await getSearchResults(search.value.val, true, true)
      return
    }

    // NB: i.e. ['one', 'two', 'three'] => { one: { two: { three: <val> }}}
    const newFilter = path.reduceRight((value, next) => ({ [next]: value }), val)
    // apply newFilter to existing filter obj
    search.value.filters = mergeWith(search.value.filters, newFilter, (existingValue, newValue) => {
      // want to overwrite arrays instead of merging them
      if (Array.isArray(existingValue)) {
        return newValue
      }
      // overwrite when new value obj is empty (obj was cleared)
      if (Object.keys(newValue).length === 0) {
        return newValue
      }
    })

    if (search.value.val) {
      const increasingScope = !hasActiveFilter()
      await getSearchResults(search.value.val, increasingScope, true)
    }
  }

  /** Get next batch of results from the api and update the results. */
  const getNextResults = async () => {
    const search = searches[searchType.value]
    if (!hasMoreResults.value) { return }
    search.value.loadingNext = true
    search.value.start += 1
    // search
    const searchResp = await callSearch()
    if (searchResp) {
      if (!searchResp.error) {
        // success
        search.value.results = [
          ...search.value.results,
          ...searchResp.searchResults.results
        ] as SearchResultI[] | RegSearchResultI[]
        search.value.error = undefined
      } else {
        search.value.start -= 1
        searchErrorHandler(searchResp.error)
      }
    } else { console.error('Error getting getNextSearchResults') } // should never get here
    search.value.loadingNext = false
  }

  /** Get the first batch of results from the api and set the results. */
  const getSearchResults = async (val: string, updateFacets = true, force = false) => {
    const search = searches[searchType.value]
    if (!val) {
      reset(searchType.value)
      return
    }
    if (!force && search.value.val === val) {
      // search for this value has already been triggered
      return
    }
    search.value.loading = true
    search.value.start = 0
    search.value.val = val
    // special case for query/roles/value
    // @ts-ignore
    search.value.filterActive = hasActiveFilter() || !!search.value.filters?.query?.roles?.value
    const searchResp = await callSearch()
    if (searchResp) {
      if (searchResp.error) {
        searchErrorHandler(searchResp.error)
      } else {
        // success
        if (val !== search.value.val) { return } // user updated the search value after this search was triggered

        if (updateFacets) {
          search.value.resultFacets = searchResp?.facets
        }

        search.value.error = undefined
        search.value.results = searchResp.searchResults.results
        search.value.resultsTotal = searchResp.searchResults.totalResults
      }
    } else {
      // unhandled response error (should never get here)
      search.value.results = []
      search.value.resultsTotal = undefined
      console.error('Nothing returned from search request fn.')
    }
    search.value.loading = false
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
    searches[type].value.filters = structuredClone(STARTING_FILTERS)
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
