// External
import { nextTick } from 'vue'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { DocumentAccessRequestHistory, SearchBar, SearchResults } from '@/components'
import { useAuth, useSearch } from '@/composables'
import { RouteNames } from '@/enums'
import { createVueRouter } from '@/router'
import store from '@/store'
import { axios } from '@/utils'
import { DashboardView } from '@/views'
// test data
import { testAccount } from './utils'


describe('DashboardView tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router
  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
  const { search, resetSearch } = useSearch()
  const { auth } = useAuth()

  sessionStorage.setItem('LEGAL_API_URL', 'http://mock-legal.ca')
  const identifier = 'BC1234567'

  beforeEach(async () => {
    const mockGet = jest.spyOn(axios, 'get')
    mockGet.mockImplementation((url) => {
      switch (url) {
        case 'purchases':
          return Promise.resolve({ data: { documentAccessRequests: [] } })
        case `businesses/${identifier}`:
          return Promise.resolve({ data: {} })
      }
    })
    auth.currentAccount = testAccount
    resetSearch()
    router = createVueRouter()
    await router.push({ name: RouteNames.SEARCH })
    wrapper = mount(DashboardView, {
      props: { appReady: true },
      global: {
        plugins: [router],
        provide: { store: store },
      },
      shallow: true  // stubs out children components
    })
    // await api calls to resolve
    await flushPromises()
  })
  afterEach(() => {
    jest.clearAllMocks();
  })
  it('renders Dashboard with expected child components', async () => {
    // check header is there
    expect(wrapper.find('h1').text()).toContain('Business Search')
    // check learn more is there
    expect(wrapper.find('.learn-more').text()).toContain('Learn More')
    expect(wrapper.find('.learn-more').attributes('href')).toContain(wrapper.vm.learnMoreURL)
    // check subheader info is there
    expect(wrapper.find('.account-label').text()).toContain(testAccount.label)
    expect(wrapper.find('.account-name').text()).toContain(testAccount.name)
    // check documents help
    expect(wrapper.find('.doc-help-btn').text()).toContain('Help with Business Search')
    expect(wrapper.find('.doc-help-info').exists()).toBe(false)
    // check tab headers
    expect(wrapper.html()).toContain('Find a Business')
    expect(wrapper.html()).toContain('View Recently Purchased Documents')
    // tab with search bar should be visible
    expect(wrapper.vm.tab).toBe('0')
    expect(wrapper.find('#search-tab').classes()).toContain('tab-item-active')
    expect(wrapper.find('#documents-tab').classes()).toContain('tab-item-inactive')
    expect(wrapper.html()).toContain('Search for businesses')
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(search.searchType).toBe('business')
    // search results should not render before a search is made
    expect(search.results).toBe(null)
    expect(search.totalResults).toBe(null)
    expect(wrapper.findComponent(SearchResults).exists()).toBe(false)
  })
  it('opens and closes document help', async () => {
    wrapper.find('.doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('.doc-help-btn').text()).toContain('Hide Help')
    expect(wrapper.find('.doc-help-info').exists()).toBe(true)
    // clicking again sets it back
    wrapper.find('.doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('.doc-help-btn').text()).toContain('Help with Business Search')
    expect(wrapper.find('.doc-help-info').exists()).toBe(false)
  })
  it('shows the results table when results are populated', async () => {
    search.results = []
    search.totalResults = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchResults).exists()).toBe(true)
  })
  it('switches tabs and displays document history table', async () => {
    wrapper.vm.tab = '1'
    await nextTick()
    expect(wrapper.find('#search-tab').classes()).toContain('tab-item-inactive')
    expect(wrapper.find('#documents-tab').classes()).toContain('tab-item-active')
    expect(wrapper.html()).toContain('This table will display up to 1000')
    expect(wrapper.findComponent(DocumentAccessRequestHistory).exists()).toBe(true)
  })
  it('pushes to business info when identifier param given', async () => {
    router = createVueRouter()
    await router.push({ name: RouteNames.SEARCH, query: { identifier: identifier } })
    wrapper = mount(DashboardView, {
      props: { appReady: false },
      global: {
        plugins: [router],
        provide: { store: store },
      },
      shallow: true  // stubs out children components
    })
    // set after to trigger watcher
    wrapper.setProps({ appReady: true })
    // await api calls to resolve
    await flushPromises()
    expect(router.currentRoute.value.name).toBe(RouteNames.BUSINESS_INFO)
  })
})
