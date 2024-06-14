import { afterEach, describe, expect, it } from 'vitest'
import { VueWrapper, flushPromises, mount } from '@vue/test-utils'

import { SearchInput } from '#components'

describe('SearchBar tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const { accessLevel, hasLimitedAccess, totalResults } = storeToRefs(search)

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
      wrapper = mount(SearchInput)
      await flushPromises()
      expect(wrapper.findComponent(SearchInput).exists()).toBe(true)
      expect(wrapper.find('[data-cy="search-input"]').exists()).toBe(true)

      // search text field is there with expected label
      const input = wrapper.find('[data-cy="search-input"]').find('input')
      expect(input.exists()).toBe(true)
      expect(input.attributes('placeholder')).toBe(option.label)

      // search bar hint
      const message = wrapper.find('p')
      expect(message.text()).toBe(option.hint)

      // radios should only show for extended search
      if (hasLimitedAccess.value) {
        expect(wrapper.find('[data-cy=search-radios]').exists()).toBe(false)
      } else {
        // update to extended and verify radios
        const radiosWrapper = wrapper.find('[data-cy=search-radios]')
        expect(radiosWrapper.exists()).toBe(true)

        const radioLabels = radiosWrapper.findAll('label')
        expect(radioLabels.length).toBe(2)
        const radioInputs = radiosWrapper.findAll('input')
        expect(radioInputs.length).toBe(2)

        // person
        expect(radioLabels[1].text()).toBe('Search People')
        expect(radioInputs[1].attributes().type).toBe('radio')
        expect(radioInputs[1].attributes().value).toBe('person')
        expect(radioInputs[1].attributes().disabled).toBeUndefined()

        // business
        expect(radioLabels[0].text()).toBe('Search Businesses')
        expect(radioInputs[0].attributes().type).toBe('radio')
        expect(radioInputs[0].attributes().value).toBe('business')
        expect(radioInputs[0].attributes().disabled).toBeUndefined()
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
      wrapper = mount(SearchInput)
      const searchTextField = wrapper.find('[data-cy="search-textfield"]')
      searchTextField.trigger('keyup.enter')
      await flushPromises()

      // validation message shows
      const message = wrapper.find('p')
      expect(message.text()).toBe(options.msg)

      // search was not triggered
      expect(totalResults.value).toBe(null)
      wrapper.unmount()
    }
  })
})
