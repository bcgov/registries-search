// External
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { StatusCodes } from 'http-status-codes'
import _ from 'lodash'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { BCRegDateRangePicker, BaseTable, ErrorRetry, SearchResults } from '@/components'
import { useAuth, useSearch } from '@/composables'
import { ErrorCategory } from '@/enums'
import { SearchEntityHeaders } from '@/resources/table-headers'
import { axios } from '@/utils'
// test data
import { SearchResponseMock, testAccount } from './utils'


describe('SearchResults tests', () => {
  let wrapper: VueWrapper<any>
  let mockPost: jest.SpyInstance<Promise<unknown>, [url: string, data?: unknown, config?: any]>

  const mockUrl = 'http://mock-url.ca'
  const mockBusinessSearchUrl = 'http://mock-search.ca'
  const mockResp = _.cloneDeep(SearchResponseMock)

  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
  sessionStorage.setItem('BOR_API_URL', mockUrl)
  sessionStorage.setItem('REGISTRIES_SEARCH_URL', mockBusinessSearchUrl)
  window['borApiKey'] = 'key'

  const { auth } = useAuth()
  auth.currentAccount = testAccount

  const { search, getSearchResults, resetSearch } = useSearch()

  beforeEach(async () => {
    mockPost = jest.spyOn(axios, 'post')
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.resolve({ data: mockResp })
      }
    })
    search.totalResults = 0
    search.results = []
    wrapper = mount(SearchResults)
    await flushPromises()
  })
  afterEach(async () => {
    resetSearch()
    jest.clearAllMocks()
    wrapper.unmount()
  })
  it('Renders and displays expected content', async () => {
    // NB: vuetify components are causing issues with wrapper.find (reason why I'm using vague .html() comparisons)
    expect(wrapper.findComponent(SearchResults).exists()).toBe(true)

    // search table is there
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)

    // renders title
    expect(wrapper.find('.base-table__title').exists()).toBe(true)
    expect(wrapper.find('.base-table__title').text()).toContain('Search Results  (0 People)')

    // renders all the headers
    const headers = wrapper.findAll('.base-table__header__item__title')
    for (const i in headers) {
      expect(SearchEntityHeaders[i].value).toEqual(headers[i].text())
    }
    // renders all the filters
    const filters = wrapper.findAll('.base-table__header__item__filter')
    let filterIndex = 0
    for (const i in SearchEntityHeaders) {
      if (!SearchEntityHeaders[i].hasFilter) continue
      const header = SearchEntityHeaders[i]
      // check filter type
      if (header.filter.type === 'select') {
        expect(filters[filterIndex].html()).toContain('v-select')
        expect(filters[filterIndex].html()).toContain(`items=""`)
        expect(filters[filterIndex].html()).toContain(`label="${header.filter.label}"`)
      } else {
        expect(filters[filterIndex].html()).toContain('v-text-field')
        expect(filters[filterIndex].html()).toContain('modelvalue=""')
        expect(filters[filterIndex].html()).toContain(`placeholder="${header.filter.label}"`)
      }
      filterIndex += 1
    }

    // datepicker filter
    expect(wrapper.find('.search-table__date-picker-filter').exists()).toBe(true)

    // renders no results found text
    expect(search.results).toEqual([])
    expect(table.find('.base-table__body__empty').exists()).toBe(true)
    expect(table.find('.base-table__body__empty').text()).toBe('No results found')

    // does not show error retry
    expect(search._error).toBe(null)
    expect(table.findComponent(ErrorRetry).exists()).toBe(false)
    // does not show load more results btn
    expect(wrapper.find('#load-more-results').find('v-btn').exists()).toBe(false)
    // does not show datepicker
    expect(wrapper.findComponent(BCRegDateRangePicker).isVisible()).toBe(false)
  })
  it('Populates data correctly results contain matches', async () => {
    // trigger search
    await getSearchResults('test')
    // sanity check
    expect(mockPost).toHaveBeenCalled()
    expect(search.totalResults).toBe(mockResp.searchResults.totalResults)
    expect(search.results.length).toBe(mockResp.searchResults.results.length)

    // check data displayed
    const table = wrapper.find('.search-table')
    // title
    expect(table.find('.base-table__title').text()).toContain('Search Results  (2 People)')
    // table item data
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(search.results.length)
    // for each row, check each column is displaying correctly
    for (const rowIndex in rows) {
      const cols = rows[rowIndex].findAll('.base-table__body__item')
      for (const i in cols) {
        if (SearchEntityHeaders[i].itemFn) {
          expect(cols[i].html()).toContain(SearchEntityHeaders[i].itemFn(search.results[rowIndex]))
          if (SearchEntityHeaders[i].col === 'legalName') {
            // if name column check it contains correct icon
            expect(cols[i].find('.search-table__icon-name').exists()).toBe(true)
            const expectedIcon = search.results[rowIndex].entityType === 'PERSON' ? 'mdi-account' : 'mdi-domain'
            expect(cols[i].find('.search-table__icon-name').text()).toContain(expectedIcon)
          } else if (SearchEntityHeaders[i].slotId === 'dates') {
            if (!search.results[rowIndex].roles[0].roleDates[0].start) {
              expect(cols[i].text()).toContain('Unknown')
            }
          }
        } else if (SearchEntityHeaders[i].slotId === 'details') {
          if (search.results[rowIndex].roles) {
            const relatedName = search.results[rowIndex].roles[0].relatedName
            const relatedIdentifier = search.results[rowIndex].roles[0].relatedIdentifier
            const relatedBN = search.results[rowIndex].roles[0].relatedBN
            expect(cols[i].text()).toBe(`${relatedName} ${relatedIdentifier} ${relatedBN || ''}`.trim())
            expect(cols[i].find('a').text()).toBe(relatedName)
            expect(cols[i].find('a').attributes().href).toBe(`${mockBusinessSearchUrl}?identifier=${relatedIdentifier}`)
          } else {
            expect(cols[i].text()).toBe('N/A')
          }
        } else if (SearchEntityHeaders[i].slotId === 'action') {
          // check action cell (should be empty)
          expect(cols[i].find('v-tooltip').exists()).toBe(false)
          expect(cols[i].text()).toBe('')
        } else {
          expect(cols[i].text()).toBe(search.results[rowIndex][SearchEntityHeaders[i].col])
        }
      }
    }
  })
  it('Shows error when a search error occurs', async () => {
    // set mock to error
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.reject({ response: { status: StatusCodes.INTERNAL_SERVER_ERROR } })
      }
    })
    // trigger search
    await getSearchResults('test')
    // sanity check -- error triggered
    expect(mockPost).toHaveBeenCalled()
    expect(search._error).not.toBe(null)
    expect(search._error.category).toBe(ErrorCategory.SEARCH)
    // check table displayed error as expected
    const table = wrapper.find('.search-table')
    expect(table.findComponent(ErrorRetry).exists()).toBe(true)
  })
  it('Error retry works as expected', async () => {
    // set mock to error
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.reject({ response: { status: StatusCodes.INTERNAL_SERVER_ERROR } })
      }
    })
    // trigger search
    await getSearchResults('test')
    // sanity check -- error triggered
    expect(mockPost).toHaveBeenCalledTimes(1)
    expect(search._error).not.toBe(null)
    expect(search._error.category).toBe(ErrorCategory.SEARCH)
    // get retry btn
    const table = wrapper.find('.search-table')
    const retry = table.findComponent(ErrorRetry).find('.error-retry__btn')
    expect(retry.exists()).toBe(true)
    // set mock back to success
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.resolve({ data: mockResp })
      }
    })
    // click retry
    retry.trigger('click')
    // it will await 1300 milliseconds
    await new Promise(resolve => setTimeout(resolve, 1400))
    await flushPromises()
    // check it called the mock and populated the table
    expect(mockPost).toHaveBeenCalledTimes(2)
    expect(search._error).toBe(null)
    expect(search.totalResults).toBe(mockResp.searchResults.totalResults)
    expect(search.results.length).toBe(mockResp.searchResults.results.length)
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(search.results.length)
  })
  it('Shows load more results button when applicable', async () => {
    // set rows asked for to 1
    sessionStorage.setItem('SEARCH_ROWS', '1')
    // set mock to one result
    mockResp.searchResults.results = [{ ...SearchResponseMock.searchResults.results[0] }]
    // assert mock total results is 2 (if this changes then code below will need to be altered)
    expect(mockResp.searchResults.totalResults).toBe(3)
    // trigger search
    await getSearchResults('test')
    // sanity check
    expect(mockPost).toHaveBeenCalledTimes(1)
    expect(search.totalResults).toBe(mockResp.searchResults.totalResults)
    expect(search.results.length).toBe(1)
    expect(wrapper.vm.hasMoreResults).toBe(true)

    // check load more results is displayed
    const moreResultsDiv = wrapper.find('#load-more-results')
    expect(moreResultsDiv.exists()).toBe(true)
    // button is there
    expect(moreResultsDiv.find('v-btn').exists()).toBe(true)

    // load more results
    // set mock for second part of response
    mockResp.searchResults.results = [
      { ...SearchResponseMock.searchResults.results[1] },
      { ...SearchResponseMock.searchResults.results[2] }
    ]
    // click load more
    moreResultsDiv.find('v-btn').trigger('click')
    // it will await 50 milliseconds
    await new Promise(resolve => setTimeout(resolve, 100))
    await flushPromises()
    // triggered call
    expect(mockPost).toHaveBeenCalledTimes(2)
    expect(search._start).toBe(1)
    // added result to existing
    expect(search.results.length).toBe(3)
    // has more results should be false
    expect(wrapper.vm.hasMoreResults).toBe(false)
    // load more button should not be there anymore
    expect(wrapper.find('#load-more-results').find('v-btn').exists()).toBe(false)

    // calling a new search should reset the start value and results
    await getSearchResults('test 2')
    expect(search._start).toBe(0)
    expect(search.results.length).toBe(2)
  })
  it('shows datepicker and executes date filtering when selected', async () => {
    wrapper.find('.search-table__date-picker-filter').trigger('click')
    await flushPromises()
    expect(wrapper.findComponent(BCRegDateRangePicker).isVisible()).toBe(true)
    // trigger a search (will allow filter change to trigger a new search)
    await getSearchResults('test')
    expect(search.filters.query.roles).toEqual({ roleDates: {} })
    expect(mockPost).toHaveBeenCalledTimes(1)
    // emit date range selection
    const startDate = new Date('2010-03-23T12:00:00')
    const endDate = new Date('2020-05-11T12:00:00')
    wrapper.findComponent(BCRegDateRangePicker).vm.$emit('submit', { endDate: endDate, startDate: startDate })
    await flushPromises()
    // check triggered search with date filter
    expect(wrapper.findComponent(BCRegDateRangePicker).isVisible()).toBe(false)
    expect(search.filters.query.roles).toEqual({ roleDates: { "end": "2020-05-11", "start": "2010-03-23" }})
    expect(mockPost).toHaveBeenCalledTimes(2)
    expect(mockPost).toHaveBeenLastCalledWith(
      "search/entities",
      {
        "categories": {"entityAddresses": {}, "entityType": ["PERSON"], "roles": {}},
        "query": {"roles": {"roleDates": {"end": "2020-05-11", "start": "2010-03-23"}}, "value": "kial"},
        "rows": 1, "start": 0
      },
      {"baseURL": "http://mock-url.ca", "headers": {"Account-Id": 1234, "x-apikey": "key"}})
  })
})
