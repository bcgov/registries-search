import { test, expect, type Locator, type Request } from '@playwright/test'
import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'

import { SearchAccess } from '../../../app/enums/search-access'
import type { BusinessSearchPayload } from '../../../app/interfaces/search-business'

test.describe('Search Business - filtering', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.PUBLIC)
  })
  test('Filtering triggers expected api calls', async ({ page }) => {
    const verifyFilterRequest = async (
      request: Promise<Request>,
      name?: string,
      identifier?: string,
      bn?: string,
      legalType?: string[],
      status?: string[]
    ) => {
      const searchRequest = await request
      const requestBody = searchRequest.postDataJSON() as BusinessSearchPayload
      expect(requestBody).toBeDefined()
      expect(requestBody.query.value).toBe('a')
      expect(requestBody.query.name).toBe(name)
      expect(requestBody.query.identifier).toBe(identifier)
      expect(requestBody.query.bn).toBe(bn)
      expect(requestBody.categories.legalType).toEqual(legalType || [])
      expect(requestBody.categories.status).toEqual(status)
    }
    const triggerTextFilter = async (filter: Locator, value: string) => {
      expect(filter).toBeVisible()
      await filter.click()
      await page.keyboard.press(value)
    }
    const triggerSelectFilter = async (filter: Locator, value: string) => {
      expect(filter).toBeVisible()
      await filter.click()
      await page.getByRole('option', { name: value }).click()
    }
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-results-table')).not.toBeVisible()
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    await page.waitForRequest('**/api/v2/search/businesses', { timeout: 5000 })
    // await page.waitForSelector('[data-testid=search-results-table]')
    expect(page.getByTestId('search-results-table')).toBeVisible()
    // header filters
    page.getByTestId('search-results-table').scrollIntoViewIfNeeded()
    const headerFilters = await page.getByTestId('search-results-table').getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(5)
    // test filter business name
    let request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    const nameFilter = headerFilters.at(0) as Locator
    await nameFilter.scrollIntoViewIfNeeded()
    const nameFilterValue = 'b'
    await triggerTextFilter(nameFilter, nameFilterValue)
    await verifyFilterRequest(request, nameFilterValue)
    // test filter identifier
    request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    const identifierFilterValue = '1'
    await triggerTextFilter(headerFilters.at(1) as Locator, identifierFilterValue)
    await verifyFilterRequest(request, nameFilterValue, identifierFilterValue)
    // test filter bn
    request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    const bnFilterValue = '0'
    await triggerTextFilter(headerFilters.at(2) as Locator, bnFilterValue)
    await verifyFilterRequest(request, nameFilterValue, identifierFilterValue, bnFilterValue)
    // test filter legal type
    request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    const legalTypeFilter = headerFilters.at(3) as Locator
    await triggerSelectFilter(legalTypeFilter, 'BC Benefit Company')
    await verifyFilterRequest(request, nameFilterValue, identifierFilterValue, bnFilterValue, ['BEN'])
    // test filter legal type - grouped option
    request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    await triggerSelectFilter(legalTypeFilter, 'BC Limited Company')
    const legalTypeFilterValue = ['C', 'BC']
    await verifyFilterRequest(request, nameFilterValue, identifierFilterValue, bnFilterValue, legalTypeFilterValue)
    // test filter status
    request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    await triggerSelectFilter(headerFilters.at(4) as Locator, 'Active')
    await verifyFilterRequest(
      request, nameFilterValue, identifierFilterValue, bnFilterValue, legalTypeFilterValue, ['ACTIVE'])
    // clear all filters
    let requestCount = 0
    page.on('request', (request) => {
      if (request.url().includes('/api/v2/search/businesses')) {
        requestCount++
      }
    })
    request = page.waitForRequest('**/api/v2/search/businesses', { timeout: 10000 })
    await page.getByTestId('search-results-table').getByTestId('search-table-clear-filters').click()
    await verifyFilterRequest(request)
    // Should have only called the api once after clearing all the filters
    expect(requestCount).toBe(1)
  })
})
