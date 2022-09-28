import { mount } from '@vue/test-utils'

import { ContactInfo } from '@/components'
import { RegistriesInfo } from '@/resources/contact-info'


describe('ContactInfo tests', () => {
  it('Displays expected content', () => {
    const wrapper = mount(ContactInfo, { props: { contacts: RegistriesInfo }})

    // verify content
    expect(wrapper.find('.contacts').exists()).toBe(true)
    const contacts = wrapper.findAll('.contacts__item')
    expect(contacts.length).toBe(RegistriesInfo.length)
    for (const i in contacts) {
      expect(contacts[i].find('.contacts__item__icon').text()).toContain(RegistriesInfo[i].icon)
      expect(contacts[i].find('label').text()).toContain(RegistriesInfo[i].label)
      expect(contacts[i].find('.contacts__item__value').text()).toContain(RegistriesInfo[i].value)
    }

    wrapper.unmount()
  })
})
