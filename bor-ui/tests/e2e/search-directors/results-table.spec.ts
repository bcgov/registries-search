import { test, expect, type Locator } from '@playwright/test'

import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'
import { SearchAccess } from '../../../app/enums/search-access'
import type { SearchResponse } from '../../../app/interfaces/search-person'
import { getSearchResultsMock } from '../../mocks/search/results/parsed-results'

test.describe('Search Directors', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.LIMITED)
  })
  test('Navigates and displays as expected in the search bar', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    // Verify search people radio
    const searchPeopleRadio = page.getByTestId('search-radios').getByRole('radio', { name: 'Search Directors' })
    expect(searchPeopleRadio).toBeVisible()
    expect(searchPeopleRadio).toBeEnabled()
    expect(searchPeopleRadio).not.toBeChecked()
    await searchPeopleRadio.click()
    expect(searchPeopleRadio).toBeChecked()
    // Verify help text etc.
    expect(page.getByTestId('search-input-info-text'))
      .toHaveText(
        'Search for the names, addresses, and business email addresses of people associated with businesses in B.C.')
    expect(page.getByTestId('search-input').getByTestId('search-textfield')).toBeVisible()
    expect(page.getByTestId('search-input').getByLabel(
      'Person Name, Address, and/or Business Email Address')).toBeVisible()
    expect(page.getByTestId('search-input')
      .getByText(
        "Example: 'John Smith', '123 Main St', 'V1V 1V1', 'John Smith Victoria', 'j.corp@123.aba'")
    ).toBeVisible()
  })

  test('Displays expected results after a search is triggered', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-results-table')).not.toBeVisible()
    // Select search people radio
    await page.getByTestId('search-radios').getByRole('radio', { name: 'Search Directors' }).click()
    // Trigger search
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    // Verify results table
    await page.waitForSelector('[data-testid=search-results-table]')
    expect(page.getByTestId('search-results-table')).toBeVisible()
    // Verify results table headers
    const headerLabels = await page.getByTestId('search-results-table').getByTestId('base-table-header').all()
    expect(headerLabels.length).toBe(7)
    expect(headerLabels.at(0) as Locator).toHaveText('Name')
    expect(headerLabels.at(1) as Locator).toHaveText('Address')
    expect(headerLabels.at(2) as Locator).toHaveText('Roles')
    expect(headerLabels.at(3) as Locator).toHaveText('Effective Dates')
    expect(headerLabels.at(4) as Locator).toHaveText('Business Details')
    expect(headerLabels.at(5) as Locator).toHaveText('Business Status')
    expect(headerLabels.at(6) as Locator).toHaveText('Business Email')
    // Verify results table filters
    const headerFilters = await page.getByTestId('search-results-table').getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(7)
    // verify results table data
    const resultsMock = getSearchResultsMock('Limited') as SearchResponse
    // title
    expect(page.getByTestId('search-results-table')
      .getByRole('heading', { name: `Search Results (${resultsMock.searchResults.totalResults} Businesses)` }))
    expect(page.getByTestId('search-results-table').getByTestId('table-export-select')).toBeVisible()
    expect(page.getByTestId('search-results-table').getByTestId('table-export-select')).toHaveText('1000')
    // rows and result data
    const resultRows = await page.getByTestId('search-results-table').getByTestId('base-table-result-row').all()
    expect(resultRows.length).toBe(resultsMock.searchResults.results.length)
    for (let i = 0; i < resultRows.length; i++) {
      const rowMockData = resultsMock.searchResults.results[i]
      const row = resultRows.at(i) as Locator
      await row.scrollIntoViewIfNeeded()
      const items = await row.getByTestId('base-table-result-row-item').all()
      // NOTE: 7 columns, but last 5 are within the same item (can have multiple inner rows within the last two cols)
      expect(items.length).toBe(3)
      // name
      expect(items.at(0) as Locator).toHaveText(rowMockData?.legalName || '')
      // address
      const address = rowMockData?.entityAddresses[0]
      expect(items.at(1) as Locator).toContainText(address?.streetAddress || '')
      expect(items.at(1) as Locator).toContainText(address?.addressCity || '')
      expect(items.at(1) as Locator).toContainText(address?.addressRegion || '')
      expect(items.at(1) as Locator).toContainText(address?.postalCode || '')
      expect(items.at(1) as Locator).toContainText(address?.addressCountry || '')
      // role columns
      const roleRows = await (items.at(2) as Locator).getByTestId('inner-row-div').all()
      expect(roleRows.length).toBe(rowMockData?.roles.length)
      for (let roleIdx = 0; roleIdx < roleRows.length; roleIdx++) {
        expect(rowMockData?.roles[roleIdx]).toBeDefined()
        const roleRowCols = await (roleRows.at(roleIdx) as Locator).getByTestId('inner-col-div').all()
        expect(roleRowCols.length).toBe(5)
        const role = rowMockData?.roles[roleIdx]
        // role type
        expect(
          (await (roleRowCols.at(0) as Locator).textContent() || '').toLowerCase())
          .toEqual((rowMockData?.roles[roleIdx]?.roleType || '').toLowerCase())
        // effective dates
        const date = role?.roleDates[0]
        if (role?.roleType === 'INCORPORATOR') {
          // Incorporators do not have an end date
          expect(roleRowCols.at(1) as Locator).toHaveText(date?.start ? date.start.substring(0, 10) : 'Unknown')
        } else {
          expect(roleRowCols.at(1) as Locator).toContainText(date?.start ? date.start.substring(0, 10) : 'Unknown')
          expect(roleRowCols.at(1) as Locator).toContainText(date?.end ? date.end.substring(0, 10) : 'Current')
        }
        // business details
        expect(roleRowCols.at(2) as Locator).toContainText(role?.relatedIdentifier || '')
        expect(roleRowCols.at(2) as Locator).toContainText(role?.relatedBN || '')
        expect(roleRowCols.at(2) as Locator).toContainText(role?.relatedName || '')
        // business status
        expect(
          (await (roleRowCols.at(3) as Locator).textContent() || '').toLowerCase())
          .toEqual((rowMockData?.roles[roleIdx]?.relatedState || '').toLowerCase())
        // business email
        expect(
          (await (roleRowCols.at(4) as Locator).textContent() || '').toLowerCase())
          .toEqual((rowMockData?.roles[roleIdx]?.relatedEmail || '').toLowerCase())
      }
    }
  })

  test('Table inner columns have the same width as their headers', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-results-table')).not.toBeVisible()
    // Select search people radio
    await page.getByTestId('search-radios').getByRole('radio', { name: 'Search Directors' }).click()
    // Trigger search
    await page.getByTestId('search-input').getByTestId('search-textfield').click()
    await page.keyboard.press('a')
    await page.waitForSelector('[data-testid=search-results-table]')
    // Get header widths
    const headerLabels = await page.getByTestId('search-results-table').getByTestId('base-table-header').all()
    expect(headerLabels.length).toBe(7)
    const headerWidth3 = (await (headerLabels.at(2) as Locator).boundingBox())?.width
    const headerWidth4 = (await (headerLabels.at(3) as Locator).boundingBox())?.width
    const headerWidth5 = (await (headerLabels.at(4) as Locator).boundingBox())?.width
    const headerWidth6 = (await (headerLabels.at(5) as Locator).boundingBox())?.width
    const headerWidth7 = (await (headerLabels.at(6) as Locator).boundingBox())?.width
    // rows and result data
    const resultRows = await page.getByTestId('base-table-result-row').all()
    expect(resultRows.length).toBeGreaterThan(0)
    for (let i = 0; i < resultRows.length; i++) {
      const row = resultRows.at(i) as Locator
      await row.scrollIntoViewIfNeeded()
      const items = await row.getByTestId('base-table-result-row-item').all()
      // NOTE: 7 columns, but last five are within the same item (can have multiple inner rows within the last two cols)
      expect(items.length).toBe(3)
      // roles (person could be associated with multiple businesses giving them multiple inner rows)
      const roleRows = await (items.at(1) as Locator).getByTestId('inner-row-div').all()
      for (let roleIdx = 0; roleIdx < roleRows.length; roleIdx++) {
        const roleRowCols = await (roleRows.at(roleIdx) as Locator).getByTestId('inner-col-div').all()
        expect(roleRowCols.length).toBe(5)
        // Verify each col is the same width as their header (within ~5 pixels)
        expect((await roleRowCols.at(0)?.boundingBox())?.width).toBeCloseTo((headerWidth3 || 0) - 4.25, 0)
        expect((await roleRowCols.at(1)?.boundingBox())?.width).toBeCloseTo((headerWidth4 || 0) - 4.25, 0)
        expect((await roleRowCols.at(2)?.boundingBox())?.width).toBeCloseTo((headerWidth5 || 0) - 4.25, 0)
        expect((await roleRowCols.at(3)?.boundingBox())?.width).toBeCloseTo((headerWidth6 || 0) - 4.25, 0)
        expect((await roleRowCols.at(3)?.boundingBox())?.width).toBeCloseTo((headerWidth7 || 0) - 4.25, 0)
      }
    }
  })
})
