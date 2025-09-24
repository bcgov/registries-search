import { test, expect, type Locator, type Request } from '@playwright/test'

import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'
import { SearchAccess } from '../../../app/enums/search-access'
import type { SearchPayload } from '../../../app/interfaces/search-person'

test.describe('Search Person - extended/filters', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.EXTENDED)
  })
  test('Triggers a search with the expected payload when updating the filter', async ({ page }) => {
    const verifyFilterRequest = async (
      request: Promise<Request>,
      name?: string | null,
      info?: string | null,
      citizenship?: string[] | null,
      roleTypes?: string[] | null
    ) => {
      const searchRequest = await request
      const requestBody = searchRequest.postDataJSON() as SearchPayload
      expect(requestBody).toBeDefined()
      expect(requestBody.query.value).toBe('a')
      expect(requestBody.query.name).toBe(name)
      expect(requestBody.query.info).toBe(info)
      expect(requestBody.categories.nationalities).toEqual(citizenship)
      expect(requestBody.categories.roles?.roleType).toEqual(roleTypes)
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
    const clearFilter = async (clearButton: Locator) => {
      expect(clearButton).toBeVisible()
      await clearButton.click()
    }
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    // Select search people radio
    const searchPeopleRadio = page.getByTestId('search-radios').getByRole('radio', { name: 'Search People' })
    await searchPeopleRadio.click()
    // Trigger search
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    await page.waitForSelector('[data-testid=search-results-table]')
    // header filters
    const headerFilters = await page.getByTestId('search-results-table').getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(7)
    // Verify name filter
    let request = page.waitForRequest('**/api/v1/search/extended', { timeout: 10000 })
    const nameFilter = headerFilters.at(0) as Locator
    await nameFilter.scrollIntoViewIfNeeded()
    const nameFilterValue = 'b'
    await triggerTextFilter(nameFilter, nameFilterValue)
    await verifyFilterRequest(request, nameFilterValue)
    // Verify info filter
    request = page.waitForRequest('**/api/v1/search/extended', { timeout: 10000 })
    const infoFilterValue = 'i'
    await triggerTextFilter(headerFilters.at(1) as Locator, infoFilterValue)
    await verifyFilterRequest(request, nameFilterValue, infoFilterValue)
    // Verify citizenship filter
    request = page.waitForRequest('**/api/v1/search/extended', { timeout: 10000 })
    const countryFilterValue = ['CA']
    await triggerSelectFilter(headerFilters.at(2) as Locator, 'Canada')
    await verifyFilterRequest(request, nameFilterValue, infoFilterValue, countryFilterValue)
    // Verify role types filter
    const roleTypeFilterValue = ['DIRECTOR']
    const roleTypeFilter = headerFilters.at(4) as Locator
    request = page.waitForRequest('**/api/v1/search/extended', { timeout: 10000 })
    await triggerSelectFilter(roleTypeFilter, 'Director')
    await verifyFilterRequest(request, nameFilterValue, infoFilterValue, countryFilterValue, roleTypeFilterValue)
    // Clear filters
    const clearButtons = await page.getByTestId('base-table-header-filter-clear').all()
    // Name
    request = page.waitForRequest('**/api/v1/search/extended', { timeout: 10000 })
    await clearFilter(clearButtons.at(0) as Locator)
    await verifyFilterRequest(request, null, infoFilterValue, countryFilterValue, roleTypeFilterValue)
    // Role Type
    request = page.waitForRequest('**/api/v1/search/extended', { timeout: 10000 })
    await clearFilter(clearButtons.at(2) as Locator)
    await verifyFilterRequest(request, null, infoFilterValue, countryFilterValue, null)
  })
})
