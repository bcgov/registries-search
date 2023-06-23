// External
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { StatusCodes } from 'http-status-codes'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { SearchBar } from '@/components'
import { useAuth, useSearch } from '@/composables'
import { ErrorCategory } from '@/enums'
import { axios } from '@/utils'
// test data
import { SearchResponseMock, testAccount } from './utils'
import { nextTick } from 'vue'


describe('SearchBar tests', () => {
  // NB: vuetify components are causing issues with wrapper.find (reason for some vague .html() comparisons)
  let wrapper: VueWrapper<any>
  let mockPost: jest.SpyInstance<Promise<unknown>, [url: string, data?: unknown, config?: any]>

  const mockUrl = 'http://mock-url.ca'
  const mockResp = { ...SearchResponseMock }

  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
  sessionStorage.setItem('BOR_API_URL', mockUrl)
  window['borApiKey'] = 'key'

  const { auth } = useAuth()
  auth.currentAccount = testAccount

  const { search, resetSearch } = useSearch()

  beforeEach(async () => {
    mockPost = jest.spyOn(axios, 'post')
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.resolve({ data: mockResp })
      }
    })
    wrapper = mount(SearchBar)
    await flushPromises()
  })
  afterEach(async () => {
    resetSearch()
    jest.clearAllMocks()
    wrapper.unmount()
  })
  it('Renders and displays expected content', async () => {
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)

    // search text field is there
    const searchTextField = wrapper.find('#search-bar-field')
    expect(searchTextField.exists()).toBe(true)
    // contains label
    const label = 'label="Director Name and/or Address'
    expect(searchTextField.html()).toContain(label)

    // search bar hint
    const hint = 'Example: &quot;John Smith&quot;, &quot;1234 St BC&quot;, &quot;VXX XXX&quot;,' +
      ' &quot;John Smith Victoria BC&quot;'
    expect(searchTextField.html()).toContain(hint)

    // validation message does NOT show
    const errorMsg = 'error-messages="Enter a name and/or address"'
    expect(searchTextField.html()).not.toContain(errorMsg)

    // checkboxes are NOT there -- this will change in the future
    const checkboxesWrapper = wrapper.find('#search-bar-checkboxes')
    expect(checkboxesWrapper.exists()).toBe(false)

    // const checkboxes = checkboxesWrapper.findAll('v-checkbox')
    // expect(checkboxes.length).toBe(2)
    
    // person
    // expect(checkboxes[0].html()).toContain('label="Person"')
    // checked
    // expect(checkboxes[0].html()).toContain('modelvalue="true"')
  
    
    // business
    // expect(checkboxes[1].html()).toContain('label="Business"')
    // not checked
    // expect(checkboxes[1].html()).toContain('modelvalue="false"')
  })
  it('Validates input', async () => {
    const searchTextField = wrapper.find('#search-bar-field')
    searchTextField.trigger('keyup.enter')
    await flushPromises()
    
    // validation message shows
    const errorMsg = 'error-messages="Enter a name and/or address"'
    expect(searchTextField.html()).toContain(errorMsg)

    // search was not triggered
    expect(search.totalResults).toBe(null)
    expect(mockPost).not.toHaveBeenCalled()
  })
  it('Triggers a search when user types in', async () => {
    const searchTerm = 'test'
    mockResp.searchResults.queryInfo.query.value = searchTerm
    // set value so that search will execute when triggered
    wrapper.vm.searchVal = searchTerm
    await nextTick()
    const searchTextField = wrapper.find('#search-bar-field')
    expect(searchTextField.html()).toContain(`modelvalue="${searchTerm}"`)
    searchTextField.trigger('keyup', { key: 't'})
    // it will await more input for half a second
    await new Promise(resolve => setTimeout(resolve, 600))
    await flushPromises()
    
    // validation message doesn't show
    const errorMsg = 'error-messages="Enter a name and/or address"'
    expect(searchTextField.html()).not.toContain(errorMsg)

    // search was triggered
    expect(search.totalResults).toBe(mockResp.searchResults.totalResults)
    expect(search._value).toBe(searchTerm)
    expect(mockPost).toHaveBeenCalled()
  })
  it('Retries if search unavailable', async () => {
    // set mock to error
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.reject({ response: { status: StatusCodes.SERVICE_UNAVAILABLE }})
      }
    })
    // set value so that search will execute when triggered
    wrapper.vm.searchVal = 'test'
    await nextTick()
    const searchTextField = wrapper.find('#search-bar-field')
    searchTextField.trigger('keyup', { key: 't'})
    // it will await more input for half a second
    await new Promise(resolve => setTimeout(resolve, 600))
    await flushPromises()
    // sanity check -- error triggered
    expect(mockPost).toHaveBeenCalledTimes(1)
    expect(search._error).not.toBe(null)
    expect(search._error.category).toBe(ErrorCategory.SEARCH_UNAVAILABLE)
    // shows attempts retry automatically after 10 seconds
    // set mock to success
    mockPost.mockImplementation((url) => {
      switch (url) {
        case 'search/entities':
          return Promise.resolve({ data: mockResp })
      }
    })
    // assert it hasn't been called again yet
    expect(mockPost).toHaveBeenCalledTimes(1)
    // wait over 10 seconds
    await new Promise(resolve => setTimeout(resolve, 11000))
    // assert it retried and got success
    expect(mockPost).toHaveBeenCalledTimes(2)
    expect(search._error).toBe(null)
    expect(search.results).toEqual(mockResp.searchResults.results)
  }, 14000)
})
