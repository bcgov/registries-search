import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { VueWrapper, flushPromises, mount } from '@vue/test-utils'

import { mockedI18n, testSearchResults } from '~~/tests/test-utils'

import {
  BaseTable,
  BcrosDateRangePicker,
  BcrosErrorRetry,
  SearchTableBusinessResults,
  SearchTablePersonResultsExtended,
  SearchTablePersonResultsLimited,
  SearchTablePersonResultsPublic,
  SearchTableResults
} from '#components'
import { SearchAccessE, type BaseTableHeaderI } from '#imports'

const verifyAddress = (text: string, address: Partial<AddressI>) => {
  expect(text).toContain(address?.addressCity || '')
  expect(text).toContain(address?.addressCountry || '')
  expect(text).toContain(address?.addressRegion || '')
  expect(text).toContain(address?.postalCode || '')
  expect(text).toContain(address?.streetAddress || '')
  expect(text).toContain(address?.streetAdditional || '')
  expect(text).toContain(address?.locationDescription || '')
  if (address?.locationDescription) {
    expect(text).toContain('Location Description')
  }
}

describe('SearchResults tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const { activeSearch, searchType, searchBusiness, searchDirector, searchPerson } = storeToRefs(search)
  const searchAccess = useBcrosSearchAccess()
  const {
    accessLevel,
    hasExtendedAccess,
    hasLimitedAccess,
    hasPublicAccess
  } = storeToRefs(searchAccess)

  const businessHeaders = getBusinessHeaders()
  const publicHeaders = getPersonHeadersPublic()
  const limitedHeaders = getPersonHeadersLimited()
  const extendedHeaders = getPersonHeadersExtended()

  const verifyDefaultSearchResultsTable = (headerConfig: BaseTableHeaderI[]) => {
    // search table is there
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)

    if (searchType.value === SearchTypeE.BUSINESS) {
      expect(wrapper.findComponent(SearchTableBusinessResults).exists()).toBe(true)
    } else if (searchType.value === SearchTypeE.DIRECTOR) {
      expect(wrapper.findComponent(SearchTablePersonResultsLimited).exists()).toBe(true)
    } else {
      expect(wrapper.findComponent(SearchTablePersonResultsPublic).exists()).toBe(hasPublicAccess.value)
      expect(wrapper.findComponent(SearchTablePersonResultsExtended).exists()).toBe(hasExtendedAccess.value)
    }
    // renders title
    expect(wrapper.find('.table-title').exists()).toBe(true)
    expect(activeSearch.value.resultsTotal).toBe(0)
    if (searchType.value === SearchTypeE.BUSINESS) {
      expect(wrapper.find('.table-title').find('h2').text()).toContain('Search Results  (0 Businesses)')
    } else {
      expect(wrapper.find('.table-title').find('h2').text()).toContain('Search Results  (0 People)')
    }
    // renders export excel stuff
    if (!hasPublicAccess.value) {
      expect(wrapper.find('[data-cy=table-export-select]').exists()).toBe(true)
      expect(wrapper.find('[data-cy=table-export-select]').text()).toContain('1000')
      expect(wrapper.find('[data-cy=table-export-btn]').exists()).toBe(true)
      expect(wrapper.find('[data-cy=table-export-btn]').text()).toContain('Export to .xlsx')
    }

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
        expect(filters[filterIndex].text()).toBe(header.filter.label)
      } else {
        expect(filters[filterIndex].find('input').attributes('placeholder')).toBe(header.filter.label)
      }
      filterIndex += 1
    }

    // renders no results found text
    expect(activeSearch.value.results).toEqual([])
    expect(table.find('.base-table__body__empty').exists()).toBe(true)
    expect(table.find('.base-table__body__empty').text()).toBe('No results found')
    // does not show error retry
    expect(activeSearch.value.error).toBeUndefined()
    expect(table.findComponent(BcrosErrorRetry).exists()).toBe(false)
    // does not show load more results btn
    expect(wrapper.find('#load-more-results').find('v-btn').exists()).toBe(false)
    if (searchType.value === SearchTypeE.BUSINESS || hasPublicAccess.value) {
      expect(wrapper.findComponent(BcrosDateRangePicker).exists()).toBe(false)
    } else {
      // does not show datepicker
      expect(wrapper.findComponent(BcrosDateRangePicker).attributes('style')).toContain('display: none;')
    }
  }

  const verifyPersonTableResults = (headerConfig: BaseTableHeaderI[]) => {
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    expect(table.find('.base-table__body__empty').exists()).toBe(false)

    // verify each row
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(testSearchResults.length)
    for (const rowIndx in rows) {
      // verify each item
      const items = rows[rowIndx].findAll('.base-table__body__row__item')
      const nonChildHeaders = headerConfig.filter(val => !val.itemHidden)
      expect(items.length).toBe(nonChildHeaders.length)
      for (const itemIndx in items) {
        const record = testSearchResults[rowIndx]
        const taxNumber = record.taxNumber
        const email = record.email
        const taxResidency = record.taxResidencies
          ? (record.taxResidencies[0] === 'CA' ? 'Canada' : 'Other')
          : undefined
        const address = record.entityAddresses ? record.entityAddresses[0] : undefined
        const countries = record.nationalities || []
        const roles = record.roles
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
        switch (nonChildHeaders[itemIndx].value) {
          case 'Name':
            expect(items[itemIndx].text()).toContain(record.legalName)
            if (hasExtendedAccess.value) {
              expect(items[itemIndx].text()).toContain(record.alternateName || '')
              expect(items[itemIndx].text()).toContain(record.birthDate || '')
              if (record.alternateName) {
                expect(items[itemIndx].text()).toContain('Preferred Name')
              }
            } else if (hasPublicAccess.value) {
              expect(items[itemIndx].text()).toContain(record.birthDate || '')
            }
            break
          case 'Address':
            verifyAddress(items[itemIndx].text(), address)
            break
          case 'Information':
            expect(items[itemIndx].text()).toContain(taxNumber || '')
            expect(items[itemIndx].text()).toContain(email || '')
            verifyAddress(items[itemIndx].text(), address)
            if (taxResidency) {
              expect(items[itemIndx].text()).toContain('Tax Residency')
            }
            break
          case 'Citizenship':
            for (const code of countries) {
              const flag = items[itemIndx].findAll('span').filter(span => span.text() === code)
              expect(flag.length).toEqual(1)
            }
            break
          case 'Business Details':
            expect(hasExtendedAccess.value || hasPublicAccess.value).toBe(true)
            for (const role of roles) {
              const roleAddress = role.relatedAddresses ? role.relatedAddresses[0] : undefined
              verifyAddress(items[itemIndx].text(), roleAddress)
              expect(items[itemIndx].text()).toContain(role.relatedBN || '')
              expect(items[itemIndx].text()).toContain(role.relatedIdentifier || '')
              expect(items[itemIndx].text()).toContain(role.relatedName || '')
              if (hasExtendedAccess.value) {
                // contains roles, control, effective dates as well
                // roles
                expect(items[itemIndx].text().toUpperCase()).toContain(role.roleType.toUpperCase())
                // control
                imgs = items[itemIndx].findAll('img')
                for (const img of imgs) {
                  expect(allAltTexts.find(altText => altText === img.attributes().alt)).not.toBe(-1)
                }
                // effective dates
                for (const role of roles) {
                  if (role.roleDates && role.roleDates.length > 0) {
                    for (const date of role.roleDates) {
                      const start = toDateStr(date.start)
                      const end = toDateStr(date.end as Date)
                      expect(items[itemIndx].text()).toContain(start || 'Unknown')
                      expect(items[itemIndx].text()).toContain(end || 'Current')
                    }
                  }
                }
              }
            }
            break
          case '': // Actions for basic should be empty
            expect(items[itemIndx].text()).toBe('')
            break
          // case 'Actions':
          //   expect(items[itemIndx].find('button').exists()).toBe(true)
          //   break
          case 'Roles':
            expect(hasLimitedAccess.value).toBe(true)
            for (const role of roles) {
              expect(items[itemIndx].text().toUpperCase()).toContain(role.roleType.toUpperCase())
              // contains effective dates, business details, business status, business email as well
              // effective dates
              for (const role of roles) {
                if (role.roleDates && role.roleDates.length > 0) {
                  for (const date of role.roleDates) {
                    const start = toDateStr(date.start)
                    const end = toDateStr(date.end as Date)
                    expect(items[itemIndx].text()).toContain(start || 'Unknown')
                    expect(items[itemIndx].text()).toContain(end || 'Current')
                  }
                }
              }
              // business details
              expect(items[itemIndx].text()).toContain(role.relatedBN || '')
              expect(items[itemIndx].text()).toContain(role.relatedIdentifier || '')
              expect(items[itemIndx].text()).toContain(role.relatedName || '')
              // business status
              expect(items[itemIndx].text().toUpperCase()).toContain(role.relatedState.toUpperCase())
              // business email
              expect(items[itemIndx].text().toUpperCase()).toContain((role.relatedEmail || '').toUpperCase())
            }
            break
          default: // Roles, Business Status, Business Email
            expect(['Roles', 'Business Status', 'Business Email'])
              .toContain(nonChildHeaders[itemIndx].value)
            for (const role of roles) {
              const roleDataMap = {
                Roles: role.roleType,
                'Business Status': role.relatedState,
                'Business Email': role.relatedEmail
              }
              expect(items[itemIndx].text().toUpperCase())
                .toContain(roleDataMap[nonChildHeaders[itemIndx].value].toUpperCase())
            }
        }
      }
    }
  }

  const MockCountryFlag = {
    template: '<span>{{ country }}</span>',
    props: ['country', 'size']
  }

  beforeEach(async () => {
    accessLevel.value = SearchAccessE.PUBLIC
    searchType.value = SearchTypeE.PERSON
    wrapper = mount(
      SearchTableResults, {
        global: {
          components: {
            CountryFlag: MockCountryFlag
          },
          plugins: [mockedI18n]
        }
      }
    )
    await flushPromises()
  })
  afterEach(() => {
    wrapper.unmount()
    search.reset(SearchTypeE.BUSINESS)
    search.reset(SearchTypeE.PERSON)
    search.reset(SearchTypeE.DIRECTOR)
  })

  it('Public Search: Renders and displays expected default content', async () => {
    expect(searchType.value).toEqual(SearchTypeE.PERSON)
    searchPerson.value.resultsTotal = 0
    await flushPromises()
    expect(activeSearch.value.results).toEqual([])
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(publicHeaders)
  })

  it('Limited Search: Renders and displays expected default content', async () => {
    accessLevel.value = SearchAccessE.LIMITED
    searchType.value = SearchTypeE.DIRECTOR
    await flushPromises()
    searchDirector.value.resultsTotal = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(limitedHeaders)
  })

  it('Extended Search: Renders and displays expected default content', async () => {
    expect(searchType.value).toEqual(SearchTypeE.PERSON)
    accessLevel.value = SearchAccessE.EXTENDED
    searchPerson.value.resultsTotal = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    // await flushPromises()
    verifyDefaultSearchResultsTable(extendedHeaders)
  })

  it('Business Search: Renders and displays expected default content', async () => {
    searchType.value = SearchTypeE.BUSINESS
    await flushPromises()
    searchBusiness.value.resultsTotal = 0
    await flushPromises()
    expect(activeSearch.value.results).toEqual([])
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(businessHeaders)
  })

  it('limited Search: Renders and displays results', async () => {
    accessLevel.value = SearchAccessE.LIMITED
    searchType.value = SearchTypeE.DIRECTOR
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    activeSearch.value.results = testSearchResults
    await flushPromises()
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    expect(table.find('.base-table__body__empty').exists()).toBe(false)
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(testSearchResults.length)
    verifyPersonTableResults(limitedHeaders)
  })

  it('Extended Search: Renders and displays results', async () => {
    expect(searchType.value).toEqual(SearchTypeE.PERSON)
    accessLevel.value = SearchAccessE.EXTENDED
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    activeSearch.value.results = testSearchResults
    await flushPromises()
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    expect(table.find('.base-table__body__empty').exists()).toBe(false)
    const rows = table.findAll('.base-table__body__row')
    expect(rows.length).toBe(testSearchResults.length)
    verifyPersonTableResults(extendedHeaders)
  })
})
