import { test, expect, type Locator } from '@playwright/test'
import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'

import { DocAccessType } from '../../../app/enums/doc-access-type'
import { SearchAccess } from '../../../app/enums/search-access'
import type { DocAccess } from '../../../app/interfaces/doc-access'
import { apiToPacificDateTime } from '../../../app/utils/date'
import { DocumentAccessRequests } from '../../mocks/search/purchases/docAccessHistory'

test.describe('Document Access History Table', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.PUBLIC)
  })
  test('Displays documents tab as expected and allows navigation to documents table', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-tabs]')
    // verify tabs
    expect(page.getByTestId('search-tabs')).toBeVisible()
    expect(page.getByTestId('search-tabs').getByRole('tab', { name: 'View Documents' })).toBeVisible()
    await page.getByTestId('search-tabs').getByRole('tab', { name: 'View Documents' }).click()
    await page.waitForSelector('[data-testid=search-docAccess]')
    expect(page.getByTestId('search-docAccess').getByTestId('search-docAccess-table')).toBeVisible()
  })

  test('Displays documents table as expected', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-tabs]')
    // Navigate to documents table
    expect(page.getByTestId('search-tabs')).toBeVisible()
    await page.getByTestId('search-tabs').getByRole('tab', { name: 'View Documents' }).click()
    await page.waitForSelector('[data-testid=search-docAccess]')
    expect(page.getByTestId('search-docAccess').getByTestId('search-docAccess-info'))
      .toHaveText('This table will display up to 1000 of the most recent document activity in the last 14 days.')
    const table = page.getByTestId('search-docAccess').getByTestId('search-docAccess-table')
    expect(table).toBeVisible()

    const docHistoryMock = DocumentAccessRequests.documentAccessRequests as DocAccess[]
    // table title
    expect(table.getByRole(
      'heading', { name: `Documents (${docHistoryMock.length})` }))
    // headers
    const headerLabels = await table.getByTestId('base-table-header').all()
    expect(headerLabels.length).toBe(6)
    expect(headerLabels.at(0) as Locator).toHaveText('Business Name')
    expect(headerLabels.at(1) as Locator).toHaveText('Number')
    expect(headerLabels.at(2) as Locator).toHaveText('Purchased Items')
    expect(headerLabels.at(3) as Locator).toHaveText('Purchased Date/Time (pacific time)')
    expect(headerLabels.at(4) as Locator).toHaveText('User Name')
    expect(headerLabels.at(5) as Locator).toHaveText('Actions')

    const headerFilters = await table.getByTestId('base-table-header-filter').all()
    expect(headerFilters.length).toBe(5)

    // rows and result data
    const resultRows = await table.getByTestId('base-table-result-row').all()
    expect(resultRows.length).toBe(docHistoryMock.length)
    for (let i = 0; i < resultRows.length; i++) {
      const rowMockData = docHistoryMock[i]
      const row = resultRows.at(i) as Locator
      await row.scrollIntoViewIfNeeded()
      const items = await row.getByTestId('base-table-result-row-item').all()
      expect(items.length).toBe(6)
      // business name
      expect(items.at(0) as Locator).toHaveText(rowMockData?.businessName?.toUpperCase() || '')
      // identifier
      expect(items.at(1) as Locator).toHaveText(rowMockData?.businessIdentifier || '')
      // documents
      for (const doc of rowMockData?.documents || []) {
        if (doc.documentType === DocAccessType.BUSINESS_SUMMARY_FILING_HISTORY) {
          expect(items.at(2) as Locator).toContainText('Business Summary')
        } else if (doc.documentType === DocAccessType.CERTIFICATE_OF_GOOD_STANDING) {
          expect(items.at(2) as Locator).toContainText('Certificate of Good Standing')
        } else if (doc.documentType === DocAccessType.CERTIFICATE_OF_STATUS) {
          expect(items.at(2) as Locator).toContainText('Certificate of Status')
        } else {
          expect(items.at(2) as Locator).toContainText('Letter Under Seal')
        }
      }
      expect(items.at(2) as Locator).toContainText('PAID')
      // date
      expect(items.at(3) as Locator).toHaveText(apiToPacificDateTime(rowMockData?.submissionDate || '') || '')
      // submitter
      expect(items.at(4) as Locator).toHaveText(rowMockData?.submitter || '')
      // view documents
      expect((items.at(5) as Locator).getByRole('button', { name: 'View Documents' })).toBeVisible()
    }
  })
})
