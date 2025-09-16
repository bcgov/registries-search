import { test, expect } from '@playwright/test'
import { mockApiCallsForPage } from '../../mocks/playwright-mock-helpers'

import { SearchAccess } from '../../../app/enums/search-access'

test.describe('Search Business - input', () => {
  test.beforeEach(async ({ page }) => {
    await mockApiCallsForPage(page, SearchAccess.PUBLIC)
  })
  test('Displays expected search bar', async ({ page }) => {
    await page.goto('/en-CA')
    await page.waitForSelector('[data-testid=search-container]')
    expect(page.getByTestId('search-input-info-text'))
      .toHaveText('Search for businesses registered or incorporated in B.C. and access their business documents.')
    expect(page.getByTestId('search-input').getByTestId('search-textfield')).toBeVisible()
    expect(page.getByTestId('search-input')
      .getByLabel('Business Name or Incorporation/Registration Number or CRA Business Number'))
      .toBeVisible()
    expect(page.getByTestId('search-input')
      .getByText("Example: 'Test Construction Inc.', 'BC0000123', '987654321BC0001'"))
      .toBeVisible()
  })
})
