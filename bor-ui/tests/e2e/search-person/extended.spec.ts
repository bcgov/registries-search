import { test, expect, type Locator } from '@playwright/test'

import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'
import { PersonControlType } from '../../../app/enums/person-control-type'
import { SearchAccess } from '../../../app/enums/search-access'
import type { SearchResponse } from '../../../app/interfaces/search-person'
import { getSearchResultsMock } from '../../mocks/search/results/parsed-results'

test.describe('Search Person - extended', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.EXTENDED)
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
      .toHaveText(
        'Search for the names, addresses, SIN/TTN/ITN, and email '
        + 'addresses of people associated with businesses in B.C.')
    expect(page.getByTestId('search-input').getByTestId('search-textfield')).toBeVisible()
    expect(page.getByTestId('search-input').getByLabel(
      'Person Name, Address, SIN/TTN/ITN, and/or Email Address')).toBeVisible()
    expect(page.getByTestId('search-input')
      .getByText(
        "Example: 'John Smith', '123 Main St', 'V1V 1V1', 'John Smith Victoria', 'j.smith@123.aba', '000 000 000'")
    ).toBeVisible()
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
    expect(headerLabels.length).toBe(7)
    expect(headerLabels.at(0) as Locator).toHaveText('Name')
    expect(headerLabels.at(1) as Locator).toHaveText('Information')
    expect(headerLabels.at(2) as Locator).toHaveText('Citizenship')
    expect(headerLabels.at(3) as Locator).toHaveText('Business Details')
    expect(headerLabels.at(4) as Locator).toHaveText('Roles')
    expect(headerLabels.at(5) as Locator).toHaveText('Details')
    expect(headerLabels.at(6) as Locator).toHaveText('Effective Dates')
    // Verify results table filters
    const headerFilters = await page.getByTestId('search-results-table').getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(7)
    // verify results table data
    const resultsMock = getSearchResultsMock('Extended') as SearchResponse
    // title
    expect(page.getByTestId('search-results-table')
      .getByRole('heading', { name: `Search Results (${resultsMock.searchResults.totalResults} Businesses)` }))
    expect(page.getByTestId('search-results-table')
      .getByTestId('table-export-select')
      .getByTestId('exportDropdown')).toBeVisible()
    expect(page.getByTestId('search-results-table')
      .getByTestId('table-export-select')
      .getByTestId('exportDropdown')).toHaveText('1000')
    // rows and result data
    const resultRows = await page.getByTestId('search-results-table').getByTestId('base-table-result-row').all()
    expect(resultRows.length).toBe(resultsMock.searchResults.results.length)
    for (let i = 0; i < resultRows.length; i++) {
      const rowMockData = resultsMock.searchResults.results[i]
      const row = resultRows.at(i) as Locator
      await row.scrollIntoViewIfNeeded()
      const items = await row.getByTestId('base-table-result-row-item').all()
      // NOTE: 7 columns, but last 4 are within the same item (can have multiple inner rows within the last two cols)
      expect(items.length).toBe(4)
      // name and birth
      expect(items.at(0) as Locator).toContainText(rowMockData?.legalName?.toUpperCase() || '')
      expect(items.at(0) as Locator).toContainText(rowMockData?.alternateName || '')
      expect(items.at(0) as Locator).toContainText(rowMockData?.birthDate || '')
      // information
      expect(items.at(1) as Locator).toContainText(rowMockData?.taxNumber || '')
      expect(items.at(1) as Locator).toContainText(rowMockData?.email || '')
      expect(items.at(1) as Locator).toContainText(rowMockData?.phoneNumber || '')
      if (rowMockData?.taxResidencies && rowMockData.taxResidencies.includes('CA')) {
        expect(items.at(1) as Locator).toContainText('Tax ResidencyCanada')
      } else if (rowMockData?.taxResidencies) {
        expect(items.at(1) as Locator).toContainText('Tax ResidencyOther')
      }
      // information - address
      const address = rowMockData?.entityAddresses[0]
      expect(items.at(1) as Locator).toContainText(address?.streetAddress || '')
      expect(items.at(1) as Locator).toContainText(address?.addressCity || '')
      expect(items.at(1) as Locator).toContainText(address?.addressRegion || '')
      expect(items.at(1) as Locator).toContainText(address?.postalCode || '')
      expect(items.at(1) as Locator).toContainText(address?.addressCountry || '')
      // citizenship
      expect(items.at(2) as Locator).toHaveText('')
      if (rowMockData?.nationalities) {
        for (const code of rowMockData.nationalities) {
          expect((items.at(2) as Locator).getByTestId(`country-flag-${code}`)).toBeVisible()
        }
      }
      const roleRows = await (items.at(3) as Locator).getByTestId('inner-row-div').all()
      expect(roleRows.length).toBe(rowMockData?.roles.length)
      for (let roleIdx = 0; roleIdx < roleRows.length; roleIdx++) {
        expect(rowMockData?.roles[roleIdx]).toBeDefined()
        const roleRowCols = await (roleRows.at(roleIdx) as Locator).getByTestId('inner-col-div').all()
        expect(roleRowCols.length).toBe(4)
        const role = rowMockData?.roles[roleIdx]
        // business details
        expect(roleRowCols.at(0) as Locator).toContainText(role?.relatedIdentifier || '')
        expect(roleRowCols.at(0) as Locator).toContainText(role?.relatedBN || '')
        expect(roleRowCols.at(0) as Locator).toContainText(role?.relatedName || '')
        if (role?.relatedAddresses) {
          const roleAddress = role.relatedAddresses[0]
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.addressCity || '')
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.addressCountry || '')
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.addressRegion || '')
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.postalCode || '')
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.streetAddress || '')
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.streetAdditional || '')
          expect(roleRowCols.at(0) as Locator).toContainText(roleAddress?.locationDescription || '')
        }
        // role type
        expect(
          (await (roleRowCols.at(1) as Locator).textContent() || '').toLowerCase())
          .toEqual((rowMockData?.roles[roleIdx]?.roleType || '').toLowerCase())
        // details
        if (role?.relatedInterests) {
          role.relatedInterests.forEach((interest) => {
            switch (interest.details) {
              case PersonControlType.DIRS_DIRECT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')).toContainText('Directors')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('control-icons-container')
                  .getByRole('img', { name: 'Direct control', exact: true }))
                break
              case PersonControlType.DIRS_SIG_INFL:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')).toContainText('Directors')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('control-icons-container')
                  .getByAltText('Significant influence control')).toBeVisible()
                break
              case PersonControlType.DIRS_INDIRECT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')).toContainText('Directors')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('control-icons-container')
                  .getByAltText('Indirect control (e.g., through another business)')).toBeVisible()
                break
              case PersonControlType.DIRS_INCONCERT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')).toContainText('Directors')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('controls-accordion')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('controls-accordion')
                  .getByTestId('controls-accordion-inConcert')).toBeVisible()
                break
              case PersonControlType.DIR_JOINTLY:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')).toContainText('Directors')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('controls-accordion')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Directors')
                  .getByTestId('controls-accordion')
                  .getByTestId('controls-accordion-jointly')).toBeVisible()
                break
              case PersonControlType.SHARES_BEN_OWNER:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')).toContainText('Shares')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('control-icons-container')
                  .getByAltText('Beneficial owner')).toBeVisible()
                break
              case PersonControlType.SHARES_INDIRECT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')).toContainText('Shares')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('control-icons-container')
                  .getByAltText('Indirect control (e.g., through another business)')).toBeVisible()
                break
              case PersonControlType.SHARES_REG_OWNER:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')).toContainText('Shares')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('control-icons-container')
                  .getByAltText('Registered owner')).toBeVisible()
                break
              case PersonControlType.SHARES_INCONCERT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')).toContainText('Shares')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('controls-accordion')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('controls-accordion')
                  .getByTestId('controls-accordion-inConcert')).toBeVisible()
                break
              case PersonControlType.SHARES_JOINTLY:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')).toContainText('Shares')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('controls-accordion')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Shares')
                  .getByTestId('controls-accordion')
                  .getByTestId('controls-accordion-jointly')).toBeVisible()
                break
              case PersonControlType.VOTES_BEN_OWNER:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')).toContainText('Votes')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('control-icons-container')
                  .getByAltText('Beneficial owner')).toBeVisible()
                break
              case PersonControlType.VOTES_INDIRECT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')).toContainText('Votes')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('control-icons-container')
                  .getByAltText('Indirect control (e.g., through another business)')).toBeVisible()
                break
              case PersonControlType.VOTES_REG_OWNER:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')).toContainText('Votes')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('control-icons-container')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('control-icons-container')
                  .getByAltText('Registered owner')).toBeVisible()
                break
              case PersonControlType.VOTES_INCONCERT:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')).toContainText('Votes')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('controls-accordion')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('controls-accordion')
                  .getByTestId('controls-accordion-inConcert')).toBeVisible()
                break
              case PersonControlType.VOTES_JOINTLY:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')).toContainText('Votes')
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('controls-accordion')).toBeVisible()
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Votes')
                  .getByTestId('controls-accordion')
                  .getByTestId('controls-accordion-jointly')).toBeVisible()
                break
              case PersonControlType.OTHER:
                expect((roleRowCols.at(2) as Locator).getByTestId('control-Other')).toHaveText('Other')
                break
              default:
                // should be one of the above
                break
            }
          })
        } else {
          expect(roleRowCols.at(2) as Locator).toHaveText('')
        }

        // dates
        const date = role?.roleDates[0]
        if (role?.roleType === 'INCORPORATOR') {
          // Incorporators do not have an end date
          expect(roleRowCols.at(3) as Locator).toHaveText(date?.start ? date.start.substring(0, 10) : 'Unknown')
        } else {
          expect(roleRowCols.at(3) as Locator).toContainText(date?.start ? date.start.substring(0, 10) : 'Unknown')
          expect(roleRowCols.at(3) as Locator).toContainText(date?.end ? date.end.substring(0, 10) : 'Current')
        }
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
    expect(headerLabels.length).toBe(7)
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
      // NOTE: 7 columns, but last 4 are within the same item (can have multiple inner rows within the last two cols)
      expect(items.length).toBe(4)
      // roles (person could be associated with multiple businesses giving them multiple inner rows)
      const roleRows = await (items.at(1) as Locator).getByTestId('inner-row-div').all()
      for (let roleIdx = 0; roleIdx < roleRows.length; roleIdx++) {
        const roleRowCols = await (roleRows.at(roleIdx) as Locator).getByTestId('inner-col-div').all()
        expect(roleRowCols.length).toBe(5)
        // Verify each col is the same width as their header (within ~5 pixels)
        expect((await roleRowCols.at(0)?.boundingBox())?.width).toBeCloseTo((headerWidth4 || 0) - 4.25, 0)
        expect((await roleRowCols.at(1)?.boundingBox())?.width).toBeCloseTo((headerWidth5 || 0) - 4.25, 0)
        expect((await roleRowCols.at(2)?.boundingBox())?.width).toBeCloseTo((headerWidth6 || 0) - 4.25, 0)
        expect((await roleRowCols.at(3)?.boundingBox())?.width).toBeCloseTo((headerWidth7 || 0) - 4.25, 0)
      }
    }
  })
})
