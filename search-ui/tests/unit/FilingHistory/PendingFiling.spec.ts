import { mount } from '@vue/test-utils'
import PendingFiling from '@/components/FilingHistory/PendingFiling.vue'
import { ContactInfo } from '@/components/common'


describe('Pending Filing', () => {
    it('Displays expected content with a null filing', () => {
        const wrapper = mount(PendingFiling, {
            props: { filing: null }
        })

        // verify content
        expect(wrapper.find('h4').exists()).toBe(false)
        expect(wrapper.findAll('p').length).toBe(0)

        wrapper.unmount()
    })

    it('Displays expected content with an empty filing', () => {
        const wrapper = mount(PendingFiling, {
            props: { filing: {} }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Filing Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('This Filing is paid')
        expect(paragraphs[1].text()).toContain('If this issue persists')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })

    it('Displays expected content with an alteration filing', () => {
        const wrapper = mount(PendingFiling, {
            props: {
                filing: {
                    name: 'alteration',
                    courtOrderNumber: 'NUMBER',
                    isArrangement: true
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Filing Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(4)
        expect(paragraphs[0].text()).toContain('This Alteration is paid')
        expect(paragraphs[1].text()).toContain('Court Order Number: NUMBER')
        expect(paragraphs[2].text()).toContain('Pursuant to a Plan of Arrangement')
        expect(paragraphs[3].text()).toContain('If this issue persists')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })

    it('Displays expected content with a filing', () => {
        const wrapper = mount(PendingFiling, {
            props: {
                filing: {
                    displayName: 'Incorporation Application'
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Filing Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('This Incorporation Application is paid')
        expect(paragraphs[1].text()).toContain('If this issue persists')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })
})
