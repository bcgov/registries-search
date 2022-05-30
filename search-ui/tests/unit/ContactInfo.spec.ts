import { mount } from '@vue/test-utils'
import { ContactInfo } from '@/components/common'


describe('Error Contact', () => {
    it('Displays expected content', () => {
        const wrapper = mount(ContactInfo)

        // verify content
        const listItems = wrapper.findAll('.contact-container')
        expect(listItems.length).toBe(3)
        expect(listItems[0].find('span').text()).toBe('Canada and U.S. Toll Free:')
        expect(listItems[0].find('.contact-value').text()).toBe('1-877-526-1526')
        expect(listItems[1].find('span').text()).toBe('Victoria Office:')
        expect(listItems[1].find('.contact-value').text()).toBe('250-952-0568')
        expect(listItems[2].find('span').text()).toBe('Email:')
        expect(listItems[2].find('.contact-value').text()).toBe('BCRegistries@gov.bc.ca')

        wrapper.unmount()
    })
})
