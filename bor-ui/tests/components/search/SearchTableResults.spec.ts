import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import BaseTable from '../../../src/components/base/table/Index.vue'
import BcrosDateRangePicker from '../../../src/components/bcros/DateRangePicker.vue'
import BcrosErrorRetry from '../../../src/components/bcros/ErrorRetry.vue'
import SearchTablePersonResults from '../../../src/components/search/table/PersonResults.vue'
import SearchTablePersonResultsExtended from '../../../src/components/search/table/PersonResultsExtended.vue'
import SearchTableResults from '../../../src/components/search/table/Results.vue'

import { testSearchResults } from '../../test-utils'
import { vuetify } from '../../setup'

describe('SearchResults tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const {
    isExtended,
    results,
    totalResults,
    searchError
  } = storeToRefs(search)

  const basicHeaders = getPersonHeaders()
  const extendedHeaders = getPersonHeadersExtended()

  const verifyDefaultSearchResultsTable = (extended: boolean) => {
    expect(isExtended.value).toBe(extended)
    // search table is there
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)

    // should be extended table NOT basic
    expect(wrapper.findComponent(SearchTablePersonResults).exists()).toBe(!extended)
    expect(wrapper.findComponent(SearchTablePersonResultsExtended).exists()).toBe(extended)

    // renders title
    expect(wrapper.find('.table-title').exists()).toBe(true)
    expect(wrapper.find('.table-title').text()).toContain('Search Results  (0 People)')

    // renders export excel stuff
    expect(wrapper.find('.search-table__export-select').exists()).toBe(true)
    expect(wrapper.find('.search-table__export-select').find('label').text()).toContain('Maximum results to export')
    expect(wrapper.find('.search-table__export-select').text()).toContain('1000')
    expect(wrapper.find('.search-table__export-rows-btn').exists()).toBe(true)
    expect(wrapper.find('.search-table__export-rows-btn').text()).toContain('Export to .xlsx')

    const headerConfig = extended ? extendedHeaders : basicHeaders
    // renders all the headers
    const headers = wrapper.findAll('.base-table__header__item__title')
    for (const i in headers) {
      expect(headerConfig[i].value).toEqual(headers[i].text())
    }
    // renders all the filters
    const filters = wrapper.findAll('.base-table__header__item__filter')
    let filterIndex = 0
    for (const i in headerConfig) {
      if (!headerConfig[i].hasFilter) {
        continue
      }
      const header = headerConfig[i]
      // check filter type
      if (header.filter.type === 'select') {
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
  }

  const verifyTableResults = (extended: boolean) => {
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    expect(table.find('.base-table__body__empty').exists()).toBe(false)

    // verify each row
    const headerConfig = extended ? extendedHeaders : basicHeaders
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(testSearchResults.length)
    for (const rowIndx in rows) {
      // verify each item
      const items = rows[rowIndx].findAll('.base-table__body__row__item')
      expect(items.length).toBe(headerConfig.length)
      for (const itemIndx in items) {
        const itemFn = headerConfig[itemIndx].itemFn
        const record = testSearchResults[rowIndx]
        const taxNumber = record.taxNumber
        const email = record.email
        const taxResidency = record.taxResidencies
          ? (record.taxResidencies[0] === 'CA' ? 'Canada' : 'Other')
          : undefined
        const address = record.entityAddresses ? record.entityAddresses[0] : undefined
        const countries = record.nationalities || []
        const role = record.roles[0]
        let imgs = []
        const allAltTexts = [
          'Beneficial owner (e.g., through a trust)',
          'Indirect control (e.g., through another business)',
          'Registered owner',
          'Other influence or control',
          'Significant influence control',
          'Indirect control (through another business)',
          'This individual has control of the majority of directors through rights and/or exercised in concert ' +
          'with other individuals',
          'Direct control'
        ]
        switch (headerConfig[itemIndx].value) {
          case 'Name':
            expect(items[itemIndx].text()).toContain(record.legalName)
            if (extended) {
              expect(items[itemIndx].text()).toContain(record.alternateName || '')
              expect(items[itemIndx].text()).toContain(record.birthDate || '')
            }
            break
          case 'Address':
            expect(items[itemIndx].text()).toContain(address?.addressCity || '')
            expect(items[itemIndx].text()).toContain(address?.addressCountry || '')
            expect(items[itemIndx].text()).toContain(address?.addressRegion || '')
            expect(items[itemIndx].text()).toContain(address?.postalCode || '')
            expect(items[itemIndx].text()).toContain(address?.streetAddress || '')
            break
          case 'Information':
            expect(items[itemIndx].text()).toContain(taxNumber || '')
            expect(items[itemIndx].text()).toContain(email || '')
            expect(items[itemIndx].text()).toContain(address?.addressCity || '')
            expect(items[itemIndx].text()).toContain(address?.addressCountry || '')
            expect(items[itemIndx].text()).toContain(address?.addressRegion || '')
            expect(items[itemIndx].text()).toContain(address?.postalCode || '')
            expect(items[itemIndx].text()).toContain(address?.streetAddress || '')
            expect(items[itemIndx].text()).toContain(taxResidency || '')
            break
          case 'Citizenship':
            for (const i in countries) {
              const code = countries[i]
              const flag = items[itemIndx].findAll('span').filter(span =>
                span.text() === code)
              expect(flag.length).toEqual(1)
            }
            break
          case 'Business Details':
            expect(items[itemIndx].text()).toContain(role.relatedBN || '')
            expect(items[itemIndx].text()).toContain(role.relatedIdentifier || '')
            expect(items[itemIndx].text()).toContain(role.relatedName || '')
            break
          case 'Details':
            imgs = items[itemIndx].findAll('img')
            for (const img of imgs) {
              expect(allAltTexts.find(altText => altText === img.attributes().alt)).not.toBe(-1)
            }
            break
          case 'Effective Dates':
            if (role.roleDates && role.roleDates.length > 0) {
              for (const i in role.roleDates) {
                const start = toDateStr(role.roleDates[i].start)
                const end = toDateStr(role.roleDates[i].end as Date)
                expect(items[itemIndx].text()).toContain(start || 'Unknown')
                expect(items[itemIndx].text()).toContain(end || 'Current')
              }
            }
            break
          case '': // Actions for basic should be empty
            expect(items[itemIndx].text()).toBe('')
            break
          case 'Actions':
            expect(items[itemIndx].find('.v-btn').exists()).toBe(true)
            break
          default: // Roles, Effective Dates, Business Status, Business Email
            expect(['Roles', 'Effective Dates', 'Business Status', 'Business Email'])
              .toContain(headerConfig[itemIndx].value)
            expect(items[itemIndx].text()).toContain(itemFn(record))
        }
      }
    }
  }

  const MockCountryFlag = {
    template: '<span>{{ country }}</span>',
    props: ['country', 'size']
  }

  beforeEach(async () => {
    totalResults.value = 0
    results.value = []
    wrapper = mount(
      SearchTableResults, {
        global: {
          plugins: [vuetify],
          components: {
            CountryFlag: MockCountryFlag
          }
        }
      }
    )
    await flushPromises()
  })
  afterEach(() => {
    search.resetSearch()
  })

  it('Basic Search: Renders and displays expected default content', () => {
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(false)
  })

  it('Extended Search: Renders and displays expected default content', async () => {
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    isExtended.value = true
    await flushPromises()
    verifyDefaultSearchResultsTable(true)
  })

  it('Basic Search: Renders and displays results', async () => {
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    isExtended.value = false
    results.value = testSearchResults
    await flushPromises()
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    expect(table.find('.base-table__body__empty').exists()).toBe(false)
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(testSearchResults.length)
    verifyTableResults(false)
  })

  it('Extended Search: Renders and displays results', async () => {
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    isExtended.value = true
    results.value = testSearchResults
    await flushPromises()
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    expect(table.find('.base-table__body__empty').exists()).toBe(false)
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(testSearchResults.length)
    verifyTableResults(true)
  })
})
