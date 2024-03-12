import { beforeEach, describe, expect, it } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'

import ContactInfo from '../../../src/components/bcros/ContactInfo.vue'
import ErrorRetry from '../../../src/components/bcros/ErrorRetry.vue'

import { vuetify } from '../../setup'

describe('ErrorRetry tests', () => {
  let wrapper: VueWrapper<any>

  let testVar = 0
  const customMsg = 'test msg'

  beforeEach(() => {
    wrapper = mount(ErrorRetry, {
      props: {
        action: (var1: number, var2: number) => (testVar = var1 + var2),
        actionArgs: [1, 2],
        message: customMsg
      },
      global: { plugins: [vuetify] }
    })
  })
  it('renders ErrorRetry', () => {
    expect(wrapper.find('.error-retry').exists()).toBe(true)
    expect(wrapper.find('.error-retry__custom-msg').exists()).toBe(true)
    expect(wrapper.find('.error-retry__base-msg').exists()).toBe(true)
    expect(wrapper.find('.error-retry__btn').exists()).toBe(true)
    expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)
  })

  it('sets given options', () => {
    expect(wrapper.find('.error-retry__custom-msg').text()).toContain(customMsg)
  })

  it('given button action works as expected', async () => {
    expect(testVar).toBe(0)
    wrapper.find('.error-retry__btn').trigger('click')
    await new Promise(resolve => setTimeout(resolve, 2000))
    expect(testVar).toBe(3)
  })
})
