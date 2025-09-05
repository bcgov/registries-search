import { afterEach, describe, expect, it } from 'vitest'
import { type VueWrapper, flushPromises, mount } from '@vue/test-utils'

import { testSearchResults, i18nMock } from '~~/tests/unit/test-utils'

import {
  BaseTable,
  DateRangePicker,
  ErrorRetry,
  SearchTableBusinessResults,
  SearchTablePersonResultsExtended,
  SearchTablePersonResultsLimited,
  SearchTablePersonResultsPublic
} from '#components'

import SearchTableResults from '../../../../app/components/search/table/Results.vue'

const verifyAddress = (text: string, address: Partial<Address>) => {
  expect(text).toContain(address?.addressCity || '')
  expect(text).toContain(address?.addressCountry || '')
  expect(text).toContain(address?.addressRegion || '')
  expect(text).toContain(address?.postalCode || '')
  expect(text).toContain(address?.streetAddress || '')
  expect(text).toContain(address?.streetAdditional || '')
  expect(text).toContain(address?.locationDescription || '')
}

describe('SearchResults tests', () => {
  let wrapper: VueWrapper<any>

  const search = useSearchStore()
  const { activeSearch, searchType, searchBusiness, searchDirector, searchPerson } = storeToRefs(search)
  const searchAccess = useSearchAccessStore()
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

  const verifyDefaultSearchResultsTable = (headerConfig: BaseTableHeader[]) => {
    // search table is there
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)

    if (searchType.value === SearchType.BUSINESS) {
      expect(wrapper.findComponent(SearchTableBusinessResults).exists()).toBe(true)
    } else if (searchType.value === SearchType.DIRECTOR) {
      expect(wrapper.findComponent(SearchTablePersonResultsLimited).exists()).toBe(true)
    } else {
      expect(wrapper.findComponent(SearchTablePersonResultsPublic).exists()).toBe(hasPublicAccess.value)
      expect(wrapper.findComponent(SearchTablePersonResultsExtended).exists()).toBe(hasExtendedAccess.value)
    }
    // renders title
    expect(wrapper.find('.table-title').exists()).toBe(true)
    expect(activeSearch.value.resultsTotal).toBe(0)
    if (searchType.value === SearchType.BUSINESS) {
      expect(wrapper.find('.table-title').find('h2').text()).toContain('Search Results  (0 Businesses)')
    } else {
      expect(wrapper.find('.table-title').find('h2').text()).toContain('Search Results  (0 People)')
    }
    // renders export excel stuff
    if (!hasPublicAccess.value) {
      expect(wrapper.find('[data-testid=table-export-select]').exists()).toBe(true)
      expect(wrapper.find('[data-testid=table-export-select]').text()).toContain('1000')
      expect(wrapper.find('[data-testid=table-export-btn]').exists()).toBe(true)
      expect(wrapper.find('[data-testid=table-export-btn]').text()).toContain('Export to .xlsx')
    }

    // renders all the headers
    const headers = wrapper.findAll('[data-testid=base-table-header]')
    for (const i in headers) {
      expect(headerConfig[i]?.value).toEqual(headers[i]?.text())
    }
    // renders all the filters
    const filters = wrapper.findAll('[data-testid="base-table-header-filter"]')
    let filterIndex = 0
    for (const i in headerConfig) {
      if (!headerConfig[i]?.hasFilter) {
        continue
      }
      const header = headerConfig[i]
      // check filter type
      if (header?.filter?.type === 'select') {
        expect(filters[filterIndex]?.text()).toBe(header?.filter?.label)
      } else {
        expect(filters[filterIndex]?.attributes('placeholder')).toBe(header?.filter?.label)
      }
      filterIndex += 1
    }

    // renders no results found text
    expect(activeSearch.value.results).toEqual([])
    expect(table.find('tbody').exists()).toBe(true)
    expect(table.find('tbody').text()).toBe('No results found')
    // does not show error retry
    expect(activeSearch.value.error).toBeUndefined()
    expect(table.findComponent(ErrorRetry).exists()).toBe(false)
    // does not show load more results btn
    expect(wrapper.find('#load-more-results').find('v-btn').exists()).toBe(false)
    if (searchType.value === SearchType.BUSINESS || hasPublicAccess.value) {
      expect(wrapper.findComponent(DateRangePicker).exists()).toBe(false)
    } else {
      // does not show datepicker
      expect(wrapper.findComponent(DateRangePicker).attributes('style')).toContain('display: none;')
    }
  }

  const verifyPersonTableResults = (headerConfig: BaseTableHeader[]) => {
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)

    // verify each row
    const rows = table.find('tbody').findAll('tr')
    expect(rows.length).toBe(testSearchResults.length)
    for (const rowIndx in rows) {
      // verify each item
      const items = rows[rowIndx]?.findAll('td')
      const nonChildHeaders = headerConfig.filter(val => !val.itemHidden)
      expect(items?.length).toBe(nonChildHeaders.length)
      for (const itemIndx in items) {
        const record = testSearchResults[rowIndx]
        const taxNumber = record?.taxNumber
        const email = record?.email
        const taxResidency = record?.taxResidencies
          ? (record.taxResidencies[0] === 'CA' ? 'Canada' : 'Other')
          : undefined
        const address = record?.entityAddresses ? record.entityAddresses[0] : undefined
        const address2 = record?.entityAddresses && record.entityAddresses.length > 1
          ? record.entityAddresses[1]
          : undefined
        // const countries = record?.nationalities || []
        const roles = record?.roles
        let imgs = []
        const allAltTexts = [
          'Beneficial owner (e.g., through a trust)',
          'Indirect control (e.g., through another business)',
          'Registered owner',
          'Other influence or control',
          'Significant influence control',
          'Indirect control (through another business)',
          'This individual has control of the majority of directors through rights and/or exercised in concert '
          + 'with other individuals',
          'Direct control'
        ]
        switch (nonChildHeaders[itemIndx].value) {
          case 'Name':
            expect(items[itemIndx].text()).toContain(record.legalName)
            if (hasExtendedAccess.value) {
              expect(items[itemIndx].text()).toContain(record.alternateName || '')
              expect(items[itemIndx].text()).toContain(record.birthDate || '')
              if (record?.alternateName) {
                expect(items[itemIndx].text()).toContain('Preferred Name')
              }
            } else if (hasPublicAccess.value) {
              expect(items[itemIndx].text()).toContain(record?.birthDate || '')
            }
            break
          case 'Address':
            verifyAddress(items[itemIndx].text(), address)
            break
          case 'Information':
            expect(items[itemIndx].text()).toContain(taxNumber || '')
            expect(items[itemIndx].text()).toContain(email || '')
            verifyAddress(items[itemIndx].text(), address)
            verifyAddress(items[itemIndx].text(), address2)
            if (taxResidency) {
              expect(items[itemIndx].text()).toContain('Tax Residency')
            }
            break
          case 'Citizenship':
            // Cannot render this due to UTooltip vitest issue. Will be secured in playwright #30180
            // for (const code of countries) {
            //   const flag = items[itemIndx].findAll('span').filter(span => span.text() === code)
            //   expect(flag.length).toEqual(1)
            // }
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
                'Roles': role.roleType,
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

  const mountResults = () => {
    const CountryFlagMock = {
      template: '<span>{{ country }}</span>',
      props: ['country', 'size']
    }
    return mount(
      SearchTableResults, {
        global: {
          components: { CountryFlag: CountryFlagMock },
          plugins: [i18nMock]
        }
      }
    )
  }
  afterEach(() => {
    wrapper.unmount()
    search.reset(SearchType.BUSINESS)
    search.reset(SearchType.PERSON)
    search.reset(SearchType.DIRECTOR)
  })

  it('Public Search: Renders and displays expected default content', async () => {
    accessLevel.value = SearchAccess.PUBLIC
    searchType.value = SearchType.PERSON
    wrapper = mountResults()
    await flushPromises()
    searchPerson.value.resultsTotal = 0
    await flushPromises()
    expect(activeSearch.value.results).toEqual([])
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(publicHeaders)
  })

  it('Limited Search: Renders and displays expected default content', async () => {
    accessLevel.value = SearchAccess.LIMITED
    searchType.value = SearchType.DIRECTOR
    wrapper = mountResults()
    await flushPromises()
    searchDirector.value.resultsTotal = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(limitedHeaders)
  })

  it('Extended Search: Renders and displays expected default content', async () => {
    accessLevel.value = SearchAccess.EXTENDED
    searchType.value = SearchType.PERSON
    wrapper = mountResults()
    await flushPromises()
    searchPerson.value.resultsTotal = 0
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    // await flushPromises()
    verifyDefaultSearchResultsTable(extendedHeaders)
  })

  it('Business Search: Renders and displays expected default content', async () => {
    accessLevel.value = SearchAccess.PUBLIC
    searchType.value = SearchType.BUSINESS
    wrapper = mountResults()
    await flushPromises()
    searchBusiness.value.resultsTotal = 0
    await flushPromises()
    expect(activeSearch.value.results).toEqual([])
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    verifyDefaultSearchResultsTable(businessHeaders)
  })

  it('limited Search: Renders and displays results', async () => {
    accessLevel.value = SearchAccess.LIMITED
    searchType.value = SearchType.DIRECTOR
    wrapper = mountResults()
    await flushPromises()
    activeSearch.value.results = testSearchResults
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    const rows = table.find('tbody').findAll('tr')
    expect(rows.length).toBe(testSearchResults.length)
    verifyPersonTableResults(limitedHeaders)
  })

  it('Extended Search: Renders and displays results', async () => {
    accessLevel.value = SearchAccess.EXTENDED
    searchType.value = SearchType.PERSON
    wrapper = mountResults()
    await flushPromises()
    activeSearch.value.results = testSearchResults
    await flushPromises()
    expect(wrapper.findComponent(SearchTableResults).exists()).toBe(true)
    // renders results in table
    const table = wrapper.find('.search-table')
    expect(table.exists()).toBe(true)
    expect(table.findComponent(BaseTable).exists()).toBe(true)
    const rows = table.find('tbody').findAll('tr')
    expect(rows.length).toBe(testSearchResults.length)
    verifyPersonTableResults(extendedHeaders)
  })
})
