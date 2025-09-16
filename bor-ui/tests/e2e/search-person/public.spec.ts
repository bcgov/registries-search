import { test, expect, type Locator } from '@playwright/test'
import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'

import { SearchAccess } from '../../../app/enums/search-access'
import type { SearchResponse } from '../../../app/interfaces/search-person'
import { getSearchResultsMock } from '../../mocks/search/results/parsed-results'

test.describe('Search Person - public', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.PUBLIC)
  })
  test('Navigates and displays as expected in the search bar', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    // Verify search people radio
    const searchPeopleRadio = page.getByTestId('search-radios').getByRole('radio', { name: 'Search People' })
    expect(searchPeopleRadio).toBeVisible()
    expect(searchPeopleRadio).toBeEnabled()
    expect(searchPeopleRadio).not.toBeChecked()
    await searchPeopleRadio.click()
    expect(searchPeopleRadio).toBeChecked()
    // Verify help text etc.
    expect(page.getByTestId('search-input-info-text'))
      .toHaveText('Search for the names of partners and proprietors associated with businesses in B.C.')
    expect(page.getByTestId('search-input').getByTestId('search-textfield')).toBeVisible()
    expect(page.getByTestId('search-input').getByLabel('Person Name')).toBeVisible()
    expect(page.getByTestId('search-input').getByText("Example: 'John Smith'")).toBeVisible()
  })

  test('Displays expected results after a search is triggered', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-results-table')).not.toBeVisible()
    // Select search people radio
    await page.getByTestId('search-radios').getByRole('radio', { name: 'Search People' }).click()
    // Trigger search
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    // Verify results table
    await page.waitForSelector('[data-testid=search-results-table]')
    expect(page.getByTestId('search-results-table')).toBeVisible()
    // Verify results table headers
    const headerLabels = await page.getByTestId('search-results-table').getByTestId('base-table-header').all()
    expect(headerLabels.length).toBe(3)
    expect(headerLabels.at(0) as Locator).toHaveText('Name')
    expect(headerLabels.at(1) as Locator).toHaveText('Business Details')
    expect(headerLabels.at(2) as Locator).toHaveText('Roles')
    // Verify results table filters
    const headerFilters = await page.getByTestId('search-results-table').getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(3)
    // verify results table data
    const resultsMock = getSearchResultsMock('Public') as SearchResponse
    // title
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
      // NOTE: 3 columns, but last two are within the same item (can have multiple inner rows within the last two cols)
      expect(items.length).toBe(2)
      // legal name and birth
      expect(items.at(0) as Locator).toContainText(rowMockData?.legalName?.toUpperCase() || '')
      expect(items.at(0) as Locator).toContainText(rowMockData?.birthDate || '')
      // roles (person could be associated with multiple businesses giving them multiple inner rows)
      const roleRows = await (items.at(1) as Locator).getByTestId('inner-row-div').all()
      expect(roleRows.length).toBe(rowMockData?.roles.length)
      for (let roleIdx = 0; roleIdx < roleRows.length; roleIdx++) {
        expect(rowMockData?.roles[roleIdx]).toBeDefined()
        const roleRowCols = await (roleRows.at(roleIdx) as Locator).getByTestId('inner-col-div').all()
        expect(roleRowCols.length).toBe(2)
        // business details
        expect(roleRowCols.at(0) as Locator).toContainText(rowMockData?.roles[roleIdx]?.relatedIdentifier || '')
        expect(roleRowCols.at(0) as Locator).toContainText(rowMockData?.roles[roleIdx]?.relatedBN || '')
        expect(roleRowCols.at(0) as Locator).toContainText(rowMockData?.roles[roleIdx]?.relatedName || '')
        // role type
        expect(
          (await (roleRowCols.at(1) as Locator).textContent() || '').toLowerCase())
          .toEqual((rowMockData?.roles[roleIdx]?.roleType || '').toLowerCase())
      }
    }
  })

  test('Table inner columns have the same width as their headers', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-results-table')).not.toBeVisible()
    // Select search people radio
    await page.getByTestId('search-radios').getByRole('radio', { name: 'Search People' }).click()
    // Trigger search
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    await page.waitForSelector('[data-testid=search-results-table]')
    // Get header widths
    const headerLabels = await page.getByTestId('search-results-table').getByTestId('base-table-header').all()
    expect(headerLabels.length).toBe(3)
    const headerWidth2 = (await (headerLabels.at(1) as Locator).boundingBox())?.width
    const headerWidth3 = (await (headerLabels.at(2) as Locator).boundingBox())?.width
    // rows and result data
    const resultRows = await page.getByTestId('base-table-result-row').all()
    expect(resultRows.length).toBeGreaterThan(0)
    for (let i = 0; i < resultRows.length; i++) {
      const row = resultRows.at(i) as Locator
      await row.scrollIntoViewIfNeeded()
      const items = await row.getByTestId('base-table-result-row-item').all()
      // NOTE: 3 columns, but last two are within the same item (can have multiple inner rows within the last two cols)
      expect(items.length).toBe(2)
      // roles (person could be associated with multiple businesses giving them multiple inner rows)
      const roleRows = await (items.at(1) as Locator).getByTestId('inner-row-div').all()
      for (let roleIdx = 0; roleIdx < roleRows.length; roleIdx++) {
        const roleRowCols = await (roleRows.at(roleIdx) as Locator).getByTestId('inner-col-div').all()
        expect(roleRowCols.length).toBe(2)
        // Verify each col is the same width as their header (within ~5 pixels)
        expect((await roleRowCols.at(0)?.boundingBox())?.width).toBeCloseTo((headerWidth2 || 0) - 4.25, 0)
        expect((await roleRowCols.at(1)?.boundingBox())?.width).toBeCloseTo((headerWidth3 || 0) - 4.25, 0)
      }
    }
  })
})
