// External
import { nextTick } from 'vue'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { DocumentAccessRequestHistory, SearchBar, SearchResults } from '@/components'
import { useSearch } from '@/composables'
import { RouteNames } from '@/enums'
import { createVueRouter } from '@/router'
import store from '@/store'
import { DashboardView } from '@/views'


describe('DashboardView tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router
  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
  const { search, resetSearch } = useSearch()

  beforeEach(async () => {
    resetSearch()
    router = createVueRouter()
    await router.push({ name: RouteNames.SEARCH })
    wrapper = mount(DashboardView, {
      props: { appReady: false },
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
    expect(wrapper.html()).toContain('Business Search')
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
})
