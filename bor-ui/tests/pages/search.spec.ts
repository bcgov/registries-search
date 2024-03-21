import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import SearchInput from '../../src/components/search/Input.vue'
import SearchTableResults from '../../src/components/search/table/Results.vue'
import Search from '../../src/pages/search.vue'

import { testAccount, testUser } from '../test-utils'

import { vuetify } from '../setup'

describe('search page tests', () => {
  let wrapper: VueWrapper<any>
  const search = useBcrosSearch()
  const { isExtended, results, totalResults } = storeToRefs(search)

  beforeEach(async () => {
    search.resetSearch()
    wrapper = mount(Search, { global: { plugins: [vuetify] } })
    // await api calls to resolve
    await flushPromises()
  })

  it('renders search page with expected child components', () => {
    expect(isExtended.value).toBe(false)
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

    const text = (
      'Search for the names, addresses, and business email ' +
      'addresses of people associated with businesses in B.C.')
    expect(wrapper.find('[data-cy="search-input-info-text"]').text()).toBe(text)
    expect(wrapper.findComponent(SearchInput).exists()).toBe(true)
    // search results should not render before a search is made
    expect(results.value).toBe(null)
    expect(totalResults.value).toBe(null)
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(false)
  })
  it('opens and closes document help', async () => {
    expect(isExtended.value).toBe(false)
    wrapper.find('#doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('#doc-help-btn').text()).toContain('Hide Help')
    expect(wrapper.find('.doc-help-info').exists()).toBe(true)
    expect(wrapper.find('.doc-help-info .doc-help-info__content').exists()).toBe(true)
    expect(wrapper.find('.doc-help-info .doc-help-info__content').text()).toContain('Help with Director Search')
    expect(wrapper.find('.doc-help-info .doc-help-info__content .learn-more').text())
      .toContain('Learn how to use Director Search - User Guide')
    expect(wrapper.find('.learn-more').attributes('href')).toContain(wrapper.vm.searchGuideURL)
    // clicking again sets it back
    wrapper.find('#doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('#doc-help-btn').text()).toContain('Help with Director Search')
    expect(wrapper.find('.doc-help-info').exists()).toBe(false)
  })
  it('shows the results table when results are populated', async () => {
    results.value = []
    totalResults.value = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
  })
  it('shows competent authority version of search when toggled', async () => {
    expect(isExtended.value).toBe(false)
    // toggle to competent authority view
    isExtended.value = true
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Business and Person Search')
    expect(wrapper.find('#doc-help-btn').text()).toContain('Help with Business and Person Search')
    wrapper.find('#doc-help-btn').trigger('click')
    await flushPromises()
    expect(wrapper.find('.doc-help-info .doc-help-info__content .learn-more').text())
      .toContain('Learn how to use Business and Person Search - User Guide')
    expect(wrapper.find('.learn-more').attributes('href')).toContain(wrapper.vm.searchGuideURL)
    const text = (
      'Search for the names, addresses, SIN/TTN/ITN, and business email ' +
      'addresses of people associated with businesses in B.C.')
    expect(wrapper.find('[data-cy="search-input-info-text"]').text()).toBe(text)
  })
})
