import { afterEach, describe, expect, it } from 'vitest'
import { VueWrapper, flushPromises, mount } from '@vue/test-utils'

import SearchInput from '../../../src/components/search/Input.vue'

import { vuetify } from '../../setup'

describe('SearchBar tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const { accessLevel, hasExtendedAccess, totalResults } = storeToRefs(search)

  afterEach(() => {
    search.resetSearch()
    accessLevel.value = SearchAccessE.PUBLIC
    wrapper?.unmount()
  })
  it('Renders and displays expected content search', async () => {
    const uiOptions = [
      { access: SearchAccessE.PUBLIC, label: 'Person Name', hint: 'Example: "John Smith"' },
      {
        access: SearchAccessE.LIMITED,
        label: 'Person Name, Address, and/or Business Email Address',
        hint: 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba"'
      },
      {
        access: SearchAccessE.EXTENDED,
        label: 'Person Name, Address, SIN/TTN/ITN, and/or Email Address',
        hint: 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba", "000 000 000"'
      }
    ]
    for (const option of uiOptions) {
      accessLevel.value = option.access
      wrapper = mount(SearchInput, { global: { plugins: [vuetify] } })
      await flushPromises()
      expect(wrapper.findComponent(SearchInput).exists()).toBe(true)

      // search text field is there with expected label
      const label = wrapper.find('label')
      expect(label.exists()).toBe(true)
      expect(label.text()).toBe(option.label)

      // search bar hint
      const message = wrapper.find('.v-messages__message')
      expect(message.text()).toBe(option.hint)

      // radios should only show for extended search
      if (!hasExtendedAccess.value) {
        expect(wrapper.find('.search-radios').exists()).toBe(false)
      } else {
        // update to extended and verify radios
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
      }
    }
  })
  it('Validates input', async () => {
    const uiOptions = [
      { access: SearchAccessE.PUBLIC, msg: 'Enter a name' },
      { access: SearchAccessE.LIMITED, msg: 'Enter a name, address, and/or business email address' },
      { access: SearchAccessE.EXTENDED, msg: 'Enter a name, address, SIN/TTN/ITN, and/or email address' }
    ]
    for (const options of uiOptions) {
      accessLevel.value = options.access
      wrapper = mount(SearchInput, { global: { plugins: [vuetify] } })
      const searchTextField = wrapper.find('#search-bar-field')
      searchTextField.trigger('keyup.enter')
      await flushPromises()

      // validation message shows
      const message = wrapper.find('.v-messages__message')
      expect(message.text()).toBe(options.msg)

      // search was not triggered
      expect(totalResults.value).toBe(null)
      wrapper.unmount()
    }
  })
})
