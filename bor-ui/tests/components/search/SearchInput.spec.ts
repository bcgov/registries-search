import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import SearchInput from '../../../src/components/search/Input.vue'

import { vuetify } from '../../setup'

describe('SearchBar tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const { isExtended, totalResults } = storeToRefs(search)

  beforeEach(() => {
    wrapper = mount(SearchInput, { global: { plugins: [vuetify] } })
  })
  afterEach(() => {
    search.resetSearch()
    isExtended.value = false
    wrapper.unmount()
  })
  it('Renders and displays expected content', async () => {
    expect(wrapper.findComponent(SearchInput).exists()).toBe(true)

    // search text field is there
    const label = wrapper.find('label')
    expect(label.exists()).toBe(true)
    // contains label
    const labelText = 'Director Name, Address, and/or Email Address'
    expect(label.text()).toBe(labelText)

    // search bar hint
    const message = wrapper.find('.v-messages__message')
    const hint = 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba"'
    expect(message.text()).toBe(hint)

    // validation message does NOT show
    const errorMsg = 'Enter a name and/or address'
    expect(wrapper.html()).not.toContain(errorMsg)

    // radios should only show for extended search
    expect(isExtended.value).toBe(false)
    expect(wrapper.find('.search-radios').exists()).toBe(false)
    // update to extended and verify radios
    isExtended.value = true
    await flushPromises()
    const radiosWrapper = wrapper.find('.search-radios')
    expect(radiosWrapper.exists()).toBe(true)

    const radios = radiosWrapper.findAll('.v-radio')
    expect(radios.length).toBe(2)

    // person
    expect(radios[1].find('label').text()).toBe('Search People')
    // selected
    expect(radios[1].find('input').attributes().type).toBe('radio')
    // have to do it by class since vuetify doesn't update the inner input value
    expect(radios[1].find('i').attributes().class).toContain('mdi-radiobox-marked mdi')
    // not disabled
    expect(radios[1].find('input').attributes().disabled).toBeUndefined()

    // business
    expect(radios[0].find('label').text()).toBe('Search Businesses')
    // not selected
    expect(radios[0].find('input').attributes().type).toBe('radio')
    // have to do it by class since vuetify doesn't update the inner input value
    expect(radios[0].find('i').attributes().class).toContain('mdi-radiobox-blank')
    // disabled (temporary)
    expect(radios[0].find('input').attributes().disabled).toBeDefined()
  })
  it('Validates input', async () => {
    const uiOptions = [
      { isExtended: false, msg: 'Enter a name, address, and/or email address' },
      { isExtended: true, msg: 'Enter a name, address, SIN/TTN/ITN, and/or email address' }
    ]
    for (const options in uiOptions) {
      isExtended.value = uiOptions[options].isExtended
      const searchTextField = wrapper.find('#search-bar-field')
      searchTextField.trigger('keyup.enter')
      await flushPromises()

      // validation message shows
      const message = wrapper.find('.v-messages__message')
      expect(message.text()).toBe(uiOptions[options].msg)

      // search was not triggered
      expect(totalResults.value).toBe(null)
    }
  })
})
