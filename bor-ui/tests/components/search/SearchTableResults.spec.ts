import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import BaseTable from '../../../src/components/base/table/Index.vue'
import BcrosDateRangePicker from '../../../src/components/bcros/DateRangePicker.vue'
import BcrosErrorRetry from '../../../src/components/bcros/ErrorRetry.vue'
import SearchTablePersonResults from '../../../src/components/search/table/PersonResults.vue'
import SearchTablePersonResultsExtended from '../../../src/components/search/table/PersonResultsExtended.vue'
import SearchTableResults from '../../../src/components/search/table/Results.vue'

import { vuetify } from '../../setup'

describe('SearchResults tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const { results, totalResults, searchError } = storeToRefs(search)

  const searchHeaders = getSearchEntityHeaders()

  beforeEach(async () => {
    totalResults.value = 0
    results.value = []
    wrapper = mount(SearchTableResults, { global: { plugins: [vuetify] } })
    await flushPromises()
  })
  afterEach(() => {
    search.resetSearch()
  })

  it('Renders and displays expected content', () => {
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)

    // search table is there
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)

    // should be basic table NOT extended
    expect(wrapper.findComponent(SearchTablePersonResults).exists()).toBe(true)
    expect(wrapper.findComponent(SearchTablePersonResultsExtended).exists()).toBe(false)

    // renders title
    expect(wrapper.find('.base-table__title').exists()).toBe(true)
    expect(wrapper.find('.base-table__title').text()).toContain('Search Results  (0 People)')

    // renders export excel stuff
    expect(wrapper.find('.search-table__export-select').exists()).toBe(true)
    expect(wrapper.find('.search-table__export-select').find('label').text()).toContain('Maximum results to export')
    expect(wrapper.find('.search-table__export-select').text()).toContain('1000')
    expect(wrapper.find('.search-table__export-rows-btn').exists()).toBe(true)
    expect(wrapper.find('.search-table__export-rows-btn').text()).toContain('Export to .xlsx')

    // renders all the headers
    const headers = wrapper.findAll('.base-table__header__item__title')
    for (const i in headers) {
      expect(searchHeaders[i].value).toEqual(headers[i].text())
    }
    // renders all the filters
    const filters = wrapper.findAll('.base-table__header__item__filter')
    let filterIndex = 0
    for (const i in searchHeaders) {
      if (!searchHeaders[i].hasFilter) { continue }
      const header = searchHeaders[i]
      // check filter type
      if (header.filter.type === 'select') {
        // expect(filters[filterIndex].html()).toContain('v-select')
        // expect(filters[filterIndex].html()).toContain(`items=""`)
        expect(filters[filterIndex].find('label').text()).toBe(header.filter.label)
      } else {
        expect(filters[filterIndex].find('input').attributes('placeholder')).toBe(header.filter.label)
      }
      filterIndex += 1
    }

    // renders no results found text
    expect(results.value).toEqual([])
    expect(table.find('.base-table__body__empty').exists()).toBe(true)
    expect(table.find('.base-table__body__empty').text()).toBe('No results found')

    // does not show error retry
    expect(searchError.value).toBe(null)
    expect(table.findComponent(BcrosErrorRetry).exists()).toBe(false)
    // does not show load more results btn
    expect(wrapper.find('#load-more-results').find('v-btn').exists()).toBe(false)
    // does not show datepicker
    expect(wrapper.findComponent(BcrosDateRangePicker).attributes('style')).toContain('display: none;')
  })
})
