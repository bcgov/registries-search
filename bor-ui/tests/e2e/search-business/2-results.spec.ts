import { test, expect, type Locator } from '@playwright/test'
import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'

import { SearchAccess } from '../../../app/enums/search-access'
import type { BusinessSearchResponse } from '../../../app/interfaces/search-business'
import { getSearchResultsMock } from '../../mocks/search/results/parsed-results'

test.describe('Search Business - results', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.PUBLIC)
  })
  test('Displays expected results after a search is triggered', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-results-table')).not.toBeVisible()
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    await page.waitForSelector('[data-testid=search-results-table]')
    expect(page.getByTestId('search-results-table')).toBeVisible()
    // headers
    const headerLabels = await page.getByTestId('search-results-table').getByTestId('base-table-header').all()
    expect(headerLabels.length).toBe(6)
    expect(headerLabels.at(0) as Locator).toHaveText('Business Name')
    expect(headerLabels.at(1) as Locator).toHaveText('Incorporation/ Registration Number')
    expect(headerLabels.at(2) as Locator).toHaveText('CRA Business Number')
    expect(headerLabels.at(3) as Locator).toHaveText('Business Type')
    expect(headerLabels.at(4) as Locator).toHaveText('Status')
    expect(headerLabels.at(5) as Locator).toHaveText('Actions')

    const headerFilters = await page.getByTestId('search-results-table').getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(5)

    // verify table results data
    const resultsMock = getSearchResultsMock('Business') as BusinessSearchResponse
    // table title
    expect(page.getByTestId('search-results-table')
      .getByRole('heading', { name: `Search Results (${resultsMock.searchResults.totalResults} Businesses)` }))
    // rows and result data
    const resultRows = await page.getByTestId('base-table-result-row').all()
    expect(resultRows.length).toBe(resultsMock.searchResults.results.length)
    for (let i = 0; i < resultRows.length; i++) {
      const rowMockData = resultsMock.searchResults.results[i]
      const row = resultRows.at(i) as Locator
      await row.scrollIntoViewIfNeeded()
      const items = await row.getByTestId('base-table-result-row-item').all()
      expect(items.length).toBe(6)
      // business name
      expect(items.at(0) as Locator).toHaveText(rowMockData?.name?.toUpperCase() || '')
      // identifier
      expect(items.at(1) as Locator).toHaveText(rowMockData?.identifier || '')
      // bn
      expect(items.at(2) as Locator).toHaveText(rowMockData?.bn || '')
      // legal type
      if (rowMockData?.legalType === 'BEN') {
        expect(items.at(3) as Locator).toHaveText('BC Benefit Company')
      } else if (rowMockData?.legalType === 'CP') {
        expect(items.at(3) as Locator).toHaveText('BC Cooperative Association')
      } else if (rowMockData?.legalType === 'SP') {
        expect(items.at(3) as Locator).toHaveText('BC Sole Proprietorship')
      } else if (rowMockData?.legalType === 'BC') {
        expect(items.at(3) as Locator).toHaveText('BC Limited Company')
      }
      // status
      if (rowMockData?.status === 'ACTIVE') {
        expect(items.at(4) as Locator).toHaveText('Active')
      } else {
        expect(items.at(4) as Locator).toHaveText('Historical')
      }
      // action button
      if (rowMockData?.modernized) {
        expect((items.at(5) as Locator).getByRole('button', { name: 'Open' })).toBeVisible()
      } else {
        expect((items.at(5) as Locator).getByRole('button', { name: 'Open' })).not.toBeVisible()
      }
    }
  })
})
