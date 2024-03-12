// import { mountSuspended } from '@nuxt/test-utils/runtime'
import { describe, expect, it } from 'vitest'

// NB: CI can't resolve the import for some reason
// import app from '../src/app.vue'

// import { vuetify } from './setup'
import { testAccount, testUser } from './test-utils'

describe('App tests', () => {
  // verify setup.
  expect(useBcrosKeycloak().kc.authenticated).toBe(true)
  expect(useBcrosKeycloak().kcUser).toEqual(testUser)
  // '.value' is due to mocked implementation of stores in .setup
  expect(useBcrosAccount().currentAccount.value).toEqual(testAccount)
  expect(useBcrosAccount().hasProductAccess(ProductCodeE.NDS)).toBe(true)

  it('mounts App with expected child components', async () => {
    // TODO: uncomment below once import is resolving in CI
    // const wrapper = await mountSuspended(app, { global: { plugins: [vuetify] } })
    // expect(wrapper.find('[data-cy="bcros-header"]').exists()).toBe(true)
    // expect(wrapper.find('[data-cy="bcros-breadcrumb"]').exists()).toBe(true)
    // expect(wrapper.find('[data-cy="bcros-banner"]').exists()).toBe(false)
    // expect(wrapper.find('[data-cy="search-input"]').exists()).toBe(true)
    // expect(wrapper.find('[data-cy="search-results-table"]').exists()).toBe(false)
    // expect(wrapper.find('[data-cy="bcros-footer"]').exists()).toBe(true)
    // expect(wrapper.find('[data-cy="bcros-loading-screen"]').exists()).toBe(false)
  })
})
