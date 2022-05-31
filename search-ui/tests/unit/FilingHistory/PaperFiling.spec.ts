import { mount } from '@vue/test-utils'
import PaperFiling from '@/components/FilingHistory/PaperFiling.vue'
import { ContactInfo } from '@/components/common'


describe('Paper Filing', () => {
    it('Displays expected content', () => {
        const wrapper = mount(PaperFiling)

        // verify content
        const paraText = wrapper.find('p').text()
        expect(paraText).toContain('This filing is available on paper only.')
        expect(paraText).toContain('To request copies of paper documents,')
        expect(paraText).toContain('contact BC Registries staff:')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })
})
