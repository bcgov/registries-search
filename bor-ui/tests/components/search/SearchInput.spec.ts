import { afterEach, describe, expect, it } from 'vitest'
import { VueWrapper, flushPromises, mount } from '@vue/test-utils'

import { SearchInput } from '#components'

describe('SearchBar tests', () => {
  let wrapper: VueWrapper<any>

  const search = useBcrosSearch()
  const { searchType, activeSearch } = storeToRefs(search)
  const searchAccess = useBcrosSearchAccess()
  const { accessLevel, hasExtendedAccess, hasLimitedAccess } = storeToRefs(searchAccess)

  afterEach(() => {
    search.reset(SearchTypeE.BUSINESS)
    search.reset(SearchTypeE.PERSON)
    search.reset(SearchTypeE.DIRECTOR)
    accessLevel.value = SearchAccessE.PUBLIC
    wrapper?.unmount()
  })
  it('Renders and displays expected content search', async () => {
    const uiOptions = [
      {
        type: SearchTypeE.BUSINESS,
        access: SearchAccessE.PUBLIC,
        label: 'Business Name or Incorporation/Registration Number or CRA Business Number',
        hint: 'Example: "Test Construction Inc.", "BC0000123", "987654321BC001"'
      },
      { type: SearchTypeE.PERSON, access: SearchAccessE.PUBLIC, label: 'Owner Name', hint: 'Example: "John Smith"' },
      {
        type: SearchTypeE.DIRECTOR,
        access: SearchAccessE.LIMITED,
        label: 'Person Name, Address, and/or Business Email Address',
        hint: 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.corp@123.aba"'
      },
      {
        type: SearchTypeE.PERSON,
        access: SearchAccessE.EXTENDED,
        label: 'Person Name, Address, SIN/TTN/ITN, and/or Email Address',
        hint: 'Example: "John Smith", "123 Main St", "V1V 1V1", "John Smith Victoria", "j.smith@123.aba", "000 000 000"'
      }
    ]
    for (const option of uiOptions) {
      searchType.value = option.type
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

      // verify radios
      const radiosWrapper = wrapper.find('[data-cy=search-radios]')
      expect(radiosWrapper.exists()).toBe(true)

      const expectedRadioNum = hasLimitedAccess.value || hasExtendedAccess.value ? 3 : 2
      const radioLabels = radiosWrapper.findAll('label')
      expect(radioLabels.length).toBe(expectedRadioNum)
      const radioInputs = radiosWrapper.findAll('input')
      expect(radioInputs.length).toBe(expectedRadioNum)

      // business
      expect(radioLabels[0].text()).toBe('Search Businesses')
      expect(radioInputs[0].attributes().type).toBe('radio')
      expect(radioInputs[0].attributes().value).toBe('business')
      expect(radioInputs[0].attributes().disabled).toBeUndefined()

      // person
      if (hasExtendedAccess.value) {
        expect(radioLabels[1].text()).toBe('Search People')
      } else {
        expect(radioLabels[1].text()).toBe('Search Owners')
      }
      expect(radioInputs[1].attributes().type).toBe('radio')
      expect(radioInputs[1].attributes().value).toBe('person')
      expect(radioInputs[1].attributes().disabled).toBeUndefined()

      // Directors
      if (hasLimitedAccess.value || hasExtendedAccess.value) {
        expect(radioLabels[2].text()).toBe('Search Directors')
        expect(radioInputs[2].attributes().type).toBe('radio')
        expect(radioInputs[2].attributes().value).toBe('director')
        expect(radioInputs[2].attributes().disabled).toBeUndefined()
      }
    }
  })
  it('Validates input', async () => {
    const uiOptions = [
      { type: SearchTypeE.BUSINESS, access: SearchAccessE.PUBLIC, msg: 'Enter a business name or number' },
      { type: SearchTypeE.PERSON, access: SearchAccessE.PUBLIC, msg: 'Enter an owner name' },
      {
        type: SearchTypeE.DIRECTOR,
        access: SearchAccessE.LIMITED,
        msg: 'Enter a name, address, and/or business email address'
      },
      {
        type: SearchTypeE.PERSON,
        access: SearchAccessE.EXTENDED,
        msg: 'Enter a name, address, SIN/TTN/ITN, and/or email address'
      }
    ]
    for (const options of uiOptions) {
      searchType.value = options.type
      accessLevel.value = options.access
      wrapper = mount(SearchInput)
      const searchTextField = wrapper.find('[data-cy="search-textfield"]')
      searchTextField.trigger('keyup.enter')
      await flushPromises()

      // validation message shows
      const message = wrapper.find('p')
      expect(message.text()).toBe(options.msg)

      // search was not triggered
      expect(activeSearch.value.resultsTotal).toBe(undefined)
      wrapper.unmount()
    }
  })
})
