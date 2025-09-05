import { beforeEach, describe, expect, it } from 'vitest'
import { type VueWrapper, mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import BaseTable from '../../../../app/components/base/table/Index.vue'

const headers: BaseTableHeader[] = [
  {
    col: 'field1',
    hasFilter: false,
    hasSort: false,
    value: 'Header 1'
  },
  {
    col: 'field2',
    hasFilter: false,
    hasSort: false,
    value: 'Header 2'
  },
  {
    col: 'key',
    hasFilter: false,
    hasSort: false,
    value: 'Header 3'
  }
]

const items = [
  {
    field1: 'row 1 col 1',
    field2: 'row 2 col 2',
    key: 'row 1 key'
  },
  {
    field1: 'row 2 col 1',
    field2: 'row 2 col 2',
    key: 'row 2 key'
  }
]

describe('BaseTable tests', () => {
  let wrapper: VueWrapper<any>

  beforeEach(() => {
    wrapper = mount(BaseTable, {
      props: {
        itemKey: 'key',
        setHeaders: headers,
        setItems: items
      }
    })
  })
  it('renders BaseTable with expected data', () => {
    expect(wrapper.find('.base-table').exists()).toBe(true)
    // header
    expect(wrapper.find('thead').exists()).toBe(true)
    expect(wrapper.find('.table-title').exists()).toBe(false)
    const headerItems = wrapper.find('thead').findAll('th')
    expect(headerItems.length).toBe(headers.length * 2) // two header rows (1 for title, 1 for filters)
    for (let i = 0; i < headers.length; i++) {
      expect(headerItems[i].text()).toContain('Header ' + (i + 1))
    }
    expect(wrapper.findAll('[data-testid="base-table-header-filter"]').length).toBe(0)
    // body
    expect(wrapper.find('tbody').exists()).toBe(true)
    const itemRows = wrapper.find('tbody').findAll('tr')
    expect(itemRows.length).toBe(items.length)
    for (let i = 0; i < itemRows.length; i++) {
      const itemCells = itemRows[i].findAll('td')
      expect(itemCells.length).toBe(headers.length)
      for (let k = 0; k < itemCells.length; k++) {
        // test each item cell value maps to specified header col
        expect(itemCells[k].text()).toBe(items[i][headers[k].col])
      }
    }
  })
  it('renders no data text', async () => {
    wrapper.setProps({
      itemKey: 'key',
      setHeaders: headers,
      setItems: []
    })
    await nextTick()
    const noDataBody1 = wrapper.find('tbody')
    expect(noDataBody1.exists()).toBe(true)
    expect(noDataBody1.text()).toContain('No results found')
    // can set via prop
    const noResultsText = 'Test custom text No results'
    wrapper.setProps({
      itemKey: 'key',
      noResultsText,
      setHeaders: headers,
      setItems: []
    })
    await nextTick()
    const noDataBody2 = wrapper.find('tbody')
    expect(noDataBody2.exists()).toBe(true)
    expect(noDataBody2.text()).toContain(noResultsText)
  })
  it('renders loading when set', async () => {
    wrapper.setProps({ loading: true })
    await nextTick()
    expect(wrapper.find('tbody').exists()).toBe(true)
    expect(wrapper.find('tbody').findAll('tr.animate-pulse').length).toBe(4)
    // updates when changed
    wrapper.setProps({ loading: false })
    await nextTick()
    expect(wrapper.find('tbody').exists()).toBe(true)
    expect(wrapper.find('tbody').find('tr.animate-pulse').exists()).toBe(false)
  })
})
