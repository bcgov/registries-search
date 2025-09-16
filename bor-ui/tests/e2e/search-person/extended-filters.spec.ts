import { test, expect, type Locator } from '@playwright/test'

import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'
import { SearchAccess } from '../../../app/enums/search-access'
import type { SearchPayload } from '../../../app/interfaces/search-person'

test.describe('Search Person - extended/filters/citizenship', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.EXTENDED)
  })
  test('Triggers a search with the expected payload when updating the filter', async ({ page }) => {
    const verifyFilterRequest = async (
      name?: string,
      info?: string,
      citizenship?: string[]
    ) => {
      const searchRequest = await page.waitForRequest('**/api/v1/search/extended', { timeout: 30000 })
      const requestBody = searchRequest.postDataJSON() as SearchPayload
      expect(requestBody).toBeDefined()
      expect(requestBody.query.value).toBe('a')
      expect(requestBody.query.name).toBe(name || '')
      expect(requestBody.query.info).toBe(info)
      expect(requestBody.categories.nationalities).toEqual(citizenship)
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
    const nameFilter = headerFilters.at(0) as Locator
    await nameFilter.scrollIntoViewIfNeeded()
    const nameFilterValue = 'b'
    await triggerTextFilter(nameFilter, nameFilterValue)
    await verifyFilterRequest(nameFilterValue)
    // Verify info filter
    const infoFilterValue = 'i'
    await triggerTextFilter(headerFilters.at(1) as Locator, infoFilterValue)
    await verifyFilterRequest(nameFilterValue, infoFilterValue)
    // Verify citizenship filter
    await triggerSelectFilter(headerFilters.at(2) as Locator, 'Canada')
    await verifyFilterRequest(nameFilterValue, infoFilterValue, ['CA'])
  })
})
