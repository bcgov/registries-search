import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'

import SearchInput from '../../../src/components/search/Input.vue'

import { vuetify } from '../../setup'

describe('SearchBar tests', () => {
  let wrapper: VueWrapper<any>

  const { search, resetSearch } = useSearch()

  beforeEach(() => {
    wrapper = mount(SearchInput, { global: { plugins: [vuetify] } })
  })
  afterEach(() => {
    resetSearch()
    wrapper.unmount()
  })
  it('Renders and displays expected content', () => {
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

    // checkboxes are NOT there -- this will change in the future
    const checkboxesWrapper = wrapper.find('#search-bar-checkboxes')
    expect(checkboxesWrapper.exists()).toBe(false)

    // const checkboxes = checkboxesWrapper.findAll('v-checkbox')
    // expect(checkboxes.length).toBe(2)

    // person
    // expect(checkboxes[0].html()).toContain('label="Person"')
    // checked
    // expect(checkboxes[0].html()).toContain('modelvalue="true"')

    // business
    // expect(checkboxes[1].html()).toContain('label="Business"')
    // not checked
    // expect(checkboxes[1].html()).toContain('modelvalue="false"')
  })
  it('Validates input', async () => {
    const searchTextField = wrapper.find('#search-bar-field')
    searchTextField.trigger('keyup.enter')
    await flushPromises()

    // validation message shows
    const message = wrapper.find('.v-messages__message')
    const errorMsg = 'Enter a name and/or address'
    expect(message.text()).toBe(errorMsg)

    // search was not triggered
    expect(search.totalResults).toBe(null)
  })
})
