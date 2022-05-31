import { mount } from '@vue/test-utils'
import CompletedAlteration from '@/components/FilingHistory/CompletedAlteration.vue'

describe('Alteration Filing', () => {
    it('Displays expected content with a null filing', () => {
        const wrapper = mount(CompletedAlteration, {
            props: { filing: null }
        })

        // verify content
        expect(wrapper.find('h4').exists()).toBe(false)
        expect(wrapper.findAll('p').length).toBe(0)

        wrapper.unmount()
    })

    it('Displays expected content with an empty filing', () => {
        const wrapper = mount(CompletedAlteration, {
            props: { filing: {} }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Alteration Complete')
        expect(wrapper.findAll('p').length).toBe(0)

        wrapper.unmount()
    })

    it('Displays expected content with a valid filing', () => {
        const wrapper = mount(CompletedAlteration, {
            props: {
                entityName: 'MY COMPANY',
                filing: {
                    fromLegalType: 'BC',
                    toLegalType: 'BEN',
                    effectiveDate: new Date('2021-01-01 08:00:00 GMT'),
                    courtOrderNumber: 'NUMBER',
                    isArrangement: true
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Alteration Complete')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(3)
        expect(paragraphs[0].text()).toContain('MY COMPANY was successfully altered')
        expect(paragraphs[0].text()).toContain('from a BC Limited Company')
        expect(paragraphs[0].text()).toContain('to a BC Benefit Company')
        expect(paragraphs[0].text()).toContain('January 1, 2021 at 12:00 am Pacific time')
        expect(paragraphs[1].text()).toContain('Court Order Number: NUMBER')
        expect(paragraphs[2].text()).toContain('Pursuant to a Plan of Arrangement')

        wrapper.unmount()
    })
})
