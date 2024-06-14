import { beforeEach, describe, expect, it } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'

import { BcrosContactInfo, BcrosErrorRetry } from '#components'

describe('ErrorRetry tests', () => {
  let wrapper: VueWrapper<any>

  let testVar = 0
  const customMsg = 'test msg'

  beforeEach(() => {
    wrapper = mount(BcrosErrorRetry, {
      props: {
        action: (var1: number, var2: number) => (testVar = var1 + var2),
        actionArgs: [1, 2],
        message: customMsg
      }
    })
  })
  it('renders ErrorRetry', () => {
    expect(wrapper.find('[data-cy="error-retry"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="error-retry-custom-msg"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="error-retry-base-msg"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="error-retry-btn"]').exists()).toBe(true)
    expect(wrapper.findComponent(BcrosContactInfo).exists()).toBe(true)
  })

  it('sets given options', () => {
    expect(wrapper.find('[data-cy="error-retry-custom-msg"]').text()).toContain(customMsg)
  })

  it('given button action works as expected', async () => {
    expect(testVar).toBe(0)
    wrapper.find('[data-cy="error-retry-btn"]').trigger('click')
    await new Promise(resolve => setTimeout(resolve, 2000))
    expect(testVar).toBe(3)
  })
})
