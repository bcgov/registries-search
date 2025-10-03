import type { Page } from '@playwright/test'

import { SearchAccess } from '../../app/enums/search-access'
import { ProductsExtended, ProductsLimited, ProductsNone, ProductsPublic } from './auth/products'
import { getUserSettingsMock } from './auth/settings'
import { LdarklyFlags } from './ldarkly/flags'
import { DocumentAccessRequests } from './search/purchases/docAccessHistory'
import { getSearchResultsMock } from './search/results/parsed-results'

export const mockApiCallsForPage = async (page: Page, accessLevel?: SearchAccess) => {
  const productsMapping = {
    [SearchAccess.EXTENDED]: ProductsExtended,
    [SearchAccess.LIMITED]: ProductsLimited,
    [SearchAccess.PUBLIC]: ProductsPublic
  }
  await page.route('**/api/v1/users/**/settings', async (route) => {
    await route.fulfill({ json: getUserSettingsMock() })
  })
  await page.route('https://app.launchdarkly.com/sdk/evalx/**/context', async (route) => {
    await route.fulfill({ json: LdarklyFlags })
  })
  await page.route('**/api/v1/orgs/**/products*', async (route) => {
    await route.fulfill({ json: accessLevel ? productsMapping[accessLevel] : ProductsNone })
  })
  await page.route('**/api/v2/purchases', async (route) => {
    await route.fulfill({ json: DocumentAccessRequests })
  })
  await page.route('**/api/v2/search/businesses', async (route) => {
    await route.fulfill({ json: getSearchResultsMock('Business') })
  })
  await page.route('**/api/v1/search/extended', async (route) => {
    if (accessLevel === SearchAccess.EXTENDED) {
      await route.fulfill({ json: getSearchResultsMock('Extended') })
    } else {
      await route.abort('accessdenied')
    }
  })
  await page.route('**/api/v1/search', async (route) => {
    if ([SearchAccess.LIMITED, SearchAccess.EXTENDED].includes(accessLevel as SearchAccess)) {
      await route.fulfill({ json: getSearchResultsMock('Limited') })
    } else {
      await route.abort('accessdenied')
    }
  })
  await page.route('**/api/v1/search/public', async (route) => {
    await route.fulfill({ json: getSearchResultsMock('Public') })
  })
}
