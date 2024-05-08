import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import AddressDisplay from '../../../src/components/bcros/AddressDisplay.vue'

describe('AddressDisplay tests', () => {
  const addressFilled: AddressI = {
    addressCity: 'Vancouver',
    addressCountry: 'Canada',
    addressRegion: 'BC',
    locationDescription: 'Cool house',
    postalCode: 'V1L 4T7',
    streetAdditional: 'Fake Park',
    streetAddress: '234 Wallaby Waffles Street'
  }

  const addressPartial: Partial<AddressI> = {
    addressCity: 'Victoria',
    addressCountry: 'Canada',
    addressRegion: 'BC',
    postalCode: 'V1K 5T8',
    streetAddress: '452 Waffles Street'
  }

  const addressMissingParts: Partial<AddressI> = {
    addressCountry: 'Canada',
    addressRegion: '',
    locationDescription: 'Find me if you can',
    postalCode: null,
    streetAddress: ''
  }
  it('Displays expected content with a filled address', () => {
    const wrapper = mount(AddressDisplay, { props: { address: addressFilled } })

    // verify content
    expect(wrapper.find('[data-cy=address-display]').exists()).toBe(true)
    const addressLines = wrapper.findAll('[data-cy=address-line]')
    expect(addressLines.length).toBe(4)
    expect(addressLines.at(0).text()).toBe(addressFilled.streetAddress)
    expect(addressLines.at(1).text()).toBe(addressFilled.streetAdditional)
    expect(addressLines.at(2).text()).toBe('Vancouver BC V1L 4T7')
    expect(addressLines.at(3).text()).toBe(addressFilled.addressCountry)
    const locDesc = wrapper.find('[data-cy=location-description]')
    expect(locDesc.exists()).toBe(true)
    expect(locDesc.find('.title').text()).toBe('Location Description')
    expect(locDesc.find('[data-cy=content]').text()).toBe(addressFilled.locationDescription)

    wrapper.unmount()
  })

  it('Displays expected content with a common partial address', () => {
    const wrapper = mount(AddressDisplay, { props: { address: addressPartial } })

    // verify content
    expect(wrapper.find('[data-cy=address-display]').exists()).toBe(true)
    const addressLines = wrapper.findAll('[data-cy=address-line]')
    expect(addressLines.length).toBe(3)
    expect(addressLines.at(0).text()).toBe(addressPartial.streetAddress)
    expect(addressLines.at(1).text()).toBe('Victoria BC V1K 5T8')
    expect(addressLines.at(2).text()).toBe(addressPartial.addressCountry)
    expect(wrapper.find('[data-cy=location-description]').exists()).toBe(false)

    wrapper.unmount()
  })

  it('Displays expected content with an address missing usual values', () => {
    const wrapper = mount(AddressDisplay, { props: { address: addressMissingParts } })

    // verify content
    expect(wrapper.find('[data-cy=address-display]').exists()).toBe(true)
    const addressLines = wrapper.findAll('[data-cy=address-line]')
    expect(addressLines.length).toBe(1)
    expect(addressLines.at(0).text()).toBe(addressMissingParts.addressCountry)
    const locDesc = wrapper.find('[data-cy=location-description]')
    expect(locDesc.exists()).toBe(true)
    expect(locDesc.find('.title').text()).toBe('Location Description')
    expect(locDesc.find('[data-cy=content]').text()).toBe(addressMissingParts.locationDescription)

    wrapper.unmount()
  })
})
