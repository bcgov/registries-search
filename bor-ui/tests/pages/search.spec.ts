import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import SearchInput from '../../src/components/search/Input.vue'
import SearchTableResults from '../../src/components/search/table/Results.vue'
import Search from '../../src/pages/search.vue'

import { testAccount, testUser } from '../test-utils'

describe('search page tests', () => {
  let wrapper: VueWrapper<any>
  const search = useBcrosSearch()
  const { activeSearch, searchType } = storeToRefs(search)

  beforeEach(async () => {
    search.reset(searchType.value)
    wrapper = mount(Search)
    // await api calls to resolve
    await flushPromises()
  })

  it('renders search page with expected child components', () => {
    // check header is there
    expect(wrapper.find('h1').text()).toBe('Business and Person Search')
    // check subheader info is there
    expect(wrapper.find('[data-cy=account-name]').text()).toContain(testAccount.label)
    expect(wrapper.find('[data-cy=user-name]').text()).toContain(testUser.fullName)
    // check documents help
    expect(wrapper.find('[data-cy="search-help-btn"]').text()).toContain('Help with Business and Person Search')
    expect(wrapper.find('.doc-help-info').exists()).toBe(false)
    // check tab headers
    expect(wrapper.find('#search-tab').exists()).toBe(false)

    const text = 'Search for businesses registered or incorporated in B.C. and access their business documents.'
    expect(wrapper.find('[data-cy="search-input-info-text"]').text()).toBe(text)
    expect(wrapper.findComponent(SearchInput).exists()).toBe(true)

    // search results should not render before a search is made
    expect(activeSearch.value.results).toEqual([])
    expect(activeSearch.value.resultsTotal).toBe(undefined)
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(false)
  })
})
