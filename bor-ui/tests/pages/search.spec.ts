import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import SearchInput from '../../src/components/search/Input.vue'
import SearchResults from '../../src/components/search/ResultsTable.vue'
import Search from '../../src/pages/search.vue'

import { testAccount, testUser } from '../test-utils'

import { vuetify } from '../setup'

describe('DashboardView tests', () => {
  let wrapper: VueWrapper<any>
  const { search, resetSearch } = useSearch()

  beforeEach(async () => {
    resetSearch()
    wrapper = mount(Search, { global: { plugins: [vuetify] } })
    // await api calls to resolve
    await flushPromises()
  })

  it('renders Dashboard with expected child components', () => {
    // check header is there
    expect(wrapper.find('h1').text()).toContain('Director Search')
    // check subheader info is there
    expect(wrapper.find('.account-label').text()).toContain(testAccount.label)
    expect(wrapper.find('.account-name').text()).toContain(testUser.fullName)
    // check documents help
    expect(wrapper.find('#doc-help-btn').text()).toContain('Help with Director Search')
    expect(wrapper.find('.doc-help-info').exists()).toBe(false)
    // check tab headers
    expect(wrapper.find('#search-tab').exists()).toBe(false)
    // expect(wrapper.html()).toContain('Find a Director')
    // tab with search bar should be visible
    // expect(wrapper.vm.tab).toBe('0')
    // expect(wrapper.find('#search-tab').classes()).not.toContain('tab-item-active')

    // check active window
    const text = (
      'Search for the names, addresses, and business email ' +
      'addresses of people associated with businesses in B.C.')
    expect(wrapper.html()).toContain(text)
    expect(wrapper.findComponent(SearchInput).exists()).toBe(true)
    // search results should not render before a search is made
    expect(search.results).toBe(null)
    expect(search.totalResults).toBe(null)
    expect(wrapper.findComponent(SearchResults).exists()).toBe(false)
  })
  it('opens and closes document help', async () => {
    wrapper.find('#doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('#doc-help-btn').text()).toContain('Hide Help')
    expect(wrapper.find('.doc-help-info').exists()).toBe(true)
    expect(wrapper.find('.doc-help-info .doc-help-info__content').exists()).toBe(true)
    expect(wrapper.find('.doc-help-info .doc-help-info__content').text()).toContain('Help with Director Search')
    expect(wrapper.find('.doc-help-info .doc-help-info__content .learn-more').text())
      .toContain('Learn how to use Director Search - User Guide')
    expect(wrapper.find('.learn-more').attributes('href')).toContain(wrapper.vm.directorSearchGuideURL)
    // clicking again sets it back
    wrapper.find('#doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('#doc-help-btn').text()).toContain('Help with Director Search')
    expect(wrapper.find('.doc-help-info').exists()).toBe(false)
  })
  it('shows the results table when results are populated', async () => {
    search.results = []
    search.totalResults = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchResults).exists()).toBe(true)
  })
})
