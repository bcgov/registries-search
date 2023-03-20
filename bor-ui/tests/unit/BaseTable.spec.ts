// External
import { nextTick } from 'vue'
import { mount, VueWrapper } from '@vue/test-utils'
// Local
import { BaseTable } from '@/components'
import { BaseTableHeaderI } from '@/interfaces/base-table'

const headers: BaseTableHeaderI[] = [
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
  },
]

describe('BaseTable tests', () => {
  let wrapper: VueWrapper<any>

  beforeEach(async () => {
    wrapper = mount(BaseTable, {
      props: {
        itemKey: 'key',
        setHeaders: headers,
        setItems: items
      }
    })
  })
  it('renders BaseTable with expected data', async () => {
    expect(wrapper.find('.base-table').exists()).toBe(true)
    // header
    expect(wrapper.find('.base-table__header').exists()).toBe(true)
    expect(wrapper.find('.base-table__title').exists()).toBe(false)
    const headerItems = wrapper.findAll('.base-table__header__item')
    expect(headerItems.length).toBe(headers.length * 2) // two header rows (1 for title, 1 for filters)
    for (let i=0; i < headers.length; i++) {
      expect(headerItems[i].text()).toContain('Header ' + (i+1))
    }
    expect(wrapper.findAll('.base-table__header__item__filter').length).toBe(0)
    // body
    expect(wrapper.find('.base-table__body').exists()).toBe(true)
    const itemRows = wrapper.findAll('.base-table__body__row')
    expect(itemRows.length).toBe(items.length)
    for (let i=0; i < itemRows.length; i++) {
      const itemCells = itemRows[i].findAll('.base-table__body__item')
      expect(itemCells.length).toBe(headers.length)
      for (let k=0; k < itemCells.length; k++) {
        // test each item cell value maps to specified header col
        expect(itemCells[k].text()).toBe(items[i][headers[k]['col']])
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
    const noDataBody1 = wrapper.find('.base-table__body__empty')
    expect(noDataBody1.exists()).toBe(true)
    expect(noDataBody1.text()).toContain('No results found')
    expect(wrapper.find('.base-table__body__row').exists()).toBe(false)
    // can set via prop
    const noResultsText = 'Test custom text No results'
    wrapper.setProps({
      itemKey: 'key',
      noResultsText: noResultsText,
      setHeaders: headers,
      setItems: []
    })
    await nextTick()
    const noDataBody2 = wrapper.find('.base-table__body__empty')
    expect(noDataBody2.exists()).toBe(true)
    expect(noDataBody2.text()).toContain(noResultsText)
  })
  it('renders loading when set', async () => {
    wrapper.setProps({ loading: true })
    await nextTick()
    expect(wrapper.find('.base-table__body__loader').exists()).toBe(true)
    expect(wrapper.find('.base-table__body__row').exists()).toBe(false)
    expect(wrapper.find('.base-table__body__empty').exists()).toBe(false)
    // updates when changed
    wrapper.setProps({ loading: false })
    await nextTick()
    expect(wrapper.find('.base-table__body__loader').exists()).toBe(false)
    expect(wrapper.find('.base-table__body__row').exists()).toBe(true)
    expect(wrapper.find('.base-table__body__empty').exists()).toBe(false)
  })
})
