import { mergeWith } from 'es-toolkit'

const DEFAULT_SEARCH_ROWS = 50

const STARTING_FILTERS: SearchPayload | BusinessSearchPayload = {
  query: {},
  categories: {}
}

/** Manages search data */
export const useSearchStore = defineStore('search', () => {
  const searchType = ref(SearchType.BUSINESS)
  // when searchType changes trigger search on new selection with current search input
  watch(searchType, (_, oldVal) => {
    getSearchResults(searches[oldVal].value.val)
  })

  const searchRows = useRuntimeConfig().public.searchRows as string

  /** Return an initialized search object based on the type. */
  const _initSearch = (type: SearchType) => {
    const filters = structuredClone(STARTING_FILTERS)

    const results = type === SearchType.BUSINESS
      ? [] as BusinessSearchResult[]
      : [] as SearchResult[]

    return ref({
      error: undefined as SearchError | undefined,
      exportRows: '1000',
      loading: false,
      loadingNext: false,
      filterActive: false,
      filters,
      resultFacets: undefined as FacetsResult | undefined,
      results,
      resultsTotal: undefined as number | undefined,
      rows: parseInt(searchRows) || DEFAULT_SEARCH_ROWS,
      start: 0,
      val: ''
    })
  }

  const searchBusiness = _initSearch(SearchType.BUSINESS)
  const searchPerson = _initSearch(SearchType.PERSON)
  const searchDirector = _initSearch(SearchType.DIRECTOR)

  const searches = {
    [SearchType.BUSINESS]: searchBusiness,
    [SearchType.PERSON]: searchPerson,
    [SearchType.DIRECTOR]: searchDirector
  }

  const activeSearch = computed(() => searches[searchType.value].value)

  /** Returns true there are more results to be returned from the api. */
  const hasMoreResults = computed(() => {
    return (
      activeSearch.value.resultsTotal
      && activeSearch.value.results.length < activeSearch.value.resultsTotal
    )
  })

  /** Returns true if any filter has a value. */
  const hasActiveFilter = () => {
    const findActiveInObject = (object: object | undefined) => {
      for (const [key, value] of Object.entries(object || {})) {
        // skip entity type filter
        if (['entityType', 'value'].includes(key)) {
          continue
        }

        if (['string', 'array'].includes(typeof (value))) {
          if (value) {
            return true
          }
        } else if (findActiveInObject(value)) {
          return true
        }
      }
      return false
    }
    return findActiveInObject(activeSearch.value.filters)
  }

  /** Call the appropriate search api based on the current state and return the response. */
  const callSearch = async (exporting = false, rows?: number) => {
    rows ??= activeSearch.value.rows
    return (searchType.value === SearchType.BUSINESS
      ? await useBusinessSearchApi()
        .searchBusiness(
          activeSearch.value.val,
          {
            ...structuredClone(toRaw(activeSearch.value.filters)),
            rows,
            start: activeSearch.value.start * rows
          } as BusinessSearchPayload
        )
      : await usePersonSearchApi()
        .searchEntities(
          activeSearch.value.val,
          {
            ...structuredClone(toRaw(activeSearch.value.filters)),
            rows,
            start: exporting ? 0 : activeSearch.value.start
          } as SearchPayload,
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
    const newFilter = toRaw(path.reduceRight((value, next) => ({ [next]: value }), val))
    // apply newFilter to existing filter obj
    search.value.filters = mergeWith(search.value.filters, newFilter, (existingValue, newValue) => {
      // want to overwrite arrays instead of merging them
      if (Array.isArray(existingValue)) {
        return newValue
      }
      // overwrite when new value obj is empty (obj was cleared)
      if (!newValue || Object.keys(newValue).length === 0) {
        return newValue || ''
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
    if (!hasMoreResults.value) {
      return
    }
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
        ] as SearchResult[] | BusinessSearchResult[]
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
    // @ts-expect-error - ts complains because roles doesn't exist on all search type filters
    search.value.filterActive = hasActiveFilter() || !!search.value.filters?.query?.roles?.value
    const searchResp = await callSearch()
    if (searchResp) {
      if (searchResp.error) {
        searchErrorHandler(searchResp.error)
      } else {
        // success
        if (val !== search.value.val) {
          return // user updated the search value after this search was triggered
        }

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
  const facetCount = (
    facet: 'entityType' | 'legalType' | 'relatedEntityType'
      | 'relatedLegalType' | 'relatedState' | 'roleType' | 'state',
    value: string
  ) => {
    const facetFields = activeSearch.value.resultFacets?.fields
    if (facetFields && Object.keys(facetFields).includes(facet)) {
      const facetItems = facetFields[facet] as Facet[]
      if (facetItems) {
        const facetItem = facetItems.find(facetItem => facetItem.value.toLowerCase() === value.toLowerCase())
        if (facetItem) {
          return facetItem.parentCount || facetItem.count
        }
      }
    }
    return 0
  }

  /** Return the list of facet items of the facet field. */
  const facetItems = (
    facet: 'entityType' | 'legalType' | 'relatedEntityType'
      | 'relatedLegalType' | 'relatedState' | 'roleType' | 'state'
  ) => {
    const facetFields = activeSearch.value.resultFacets?.fields
    if (facetFields && Object.keys(facetFields).includes(facet)) {
      return facetFields[facet] as Facet[] || []
    }
    return []
  }

  /** Return the highlighted search value within the match */
  const highlightMatch = (match: string) => {
    if (!activeSearch.value.val) {
      return match
    }
    if (!match) {
      return ''
    }
    return match.replaceAll(activeSearch.value.val.toUpperCase(), `<b>${activeSearch.value.val.toUpperCase()}</b>`)
  }

  const searchErrorHandler = (error: SearchError) => {
    console.error(error)
    activeSearch.value.resultsTotal = undefined
    activeSearch.value.error = error
  }

  const reset = (type: SearchType) => {
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
