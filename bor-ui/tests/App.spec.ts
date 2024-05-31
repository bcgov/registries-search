// import { mountSuspended } from '@nuxt/test-utils/runtime'
import { describe, expect } from 'vitest'

// NB: CI can't resolve the import for some reason
// import app from '../src/app.vue'

import { testAccount, testUser } from './test-utils'

describe('App tests', () => {
  it('verify setup', () => {
    expect(useBcrosKeycloak().kc.authenticated).toBe(true)
    expect(useBcrosKeycloak().kcUser).toEqual(testUser)
    // '.value' is due to mocked implementation of stores in .setup
    expect(useBcrosAccount().currentAccount.value).toEqual(testAccount)
    expect(useBcrosAccount().hasProductAccess(ProductCodeE.NDS)).toBe(false)
  })
})
