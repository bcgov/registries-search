/* eslint max-len: 0 */
import { mount } from '@vue/test-utils'
import FutureEffectivePending from '@/components/FilingHistory/FutureEffectivePending.vue'
import { ContactInfo } from '@/components/common'

describe('Future Effective Pending', () => {
    it('Displays expected content with a null filing', () => {
        const wrapper = mount(FutureEffectivePending, {
            props: { filing: null }
        })

        // verify content
        expect(wrapper.findAll('p').length).toEqual(0)

        wrapper.unmount()
    })

    it('Displays expected content with an empty filing', () => {
        const wrapper = mount(FutureEffectivePending, {
            props: { filing: {} }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Filing Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('The filing date and time for this company')
        expect(paragraphs[0].text()).toContain('has been recorded as Unknown.')
        expect(paragraphs[1].text()).toContain('It may take up to one hour to process this filing. If this issue persists,')
        expect(paragraphs[1].text()).toContain('please contact us.')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })

    it('Displays expected content with a FE named IA', () => {
        const wrapper = mount(FutureEffectivePending, {
            props: {
                entityName: 'My Incorporation',
                filing: {
                    isFutureEffectiveIaPending: true,
                    effectiveDate: new Date('2020-05-15 19:00:00 GMT')
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Incorporation Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('The incorporation date and time for My Incorporation')
        expect(paragraphs[0].text()).toContain('has been recorded as May 15, 2020 at 12:00 pm Pacific time.')
        expect(paragraphs[1].text()).toContain('It may take up to one hour to process this filing. If this issue persists,')
        expect(paragraphs[1].text()).toContain('please contact us.')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })

    it('Displays expected content with a FE numbered IA', () => {

        const wrapper = mount(FutureEffectivePending, {
            props: {
                entityName: '',
                filing: {
                    isFutureEffectiveIaPending: true,
                    effectiveDate: new Date('2020-05-15 19:00:00 GMT')
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Incorporation Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(2)
        expect(paragraphs[0].text()).toContain('The incorporation date and time for this company')
        expect(paragraphs[0].text()).toContain('has been recorded as May 15, 2020 at 12:00 pm Pacific time.')
        expect(paragraphs[1].text()).toContain('It may take up to one hour to process this filing. If this issue persists,')
        expect(paragraphs[1].text()).toContain('please contact us.')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })

    it('Displays expected content with a FE Alteration', () => {
        const wrapper = mount(FutureEffectivePending, {

            props: {
                entityName: 'My Alteration',
                filing: {
                    isFutureEffectiveAlterationPending: true,
                    effectiveDate: new Date('2020-05-15 19:00:00 GMT'),
                    courtOrderNumber: '123',
                    isArrangement: true
                }
            }
        })

        // verify content
        expect(wrapper.find('h4').text()).toBe('Alteration Pending')
        const paragraphs = wrapper.findAll('p')
        expect(paragraphs.length).toBe(4)
        expect(paragraphs[0].text()).toContain('The alteration date and time for My Alteration')
        expect(paragraphs[0].text()).toContain('has been recorded as May 15, 2020 at 12:00 pm Pacific time.')
        expect(paragraphs[1].text()).toContain('Court Order Number: 123')
        expect(paragraphs[2].text()).toContain('Pursuant to a Plan of Arrangement')
        expect(paragraphs[3].text()).toContain('It may take up to one hour to process this filing. If this issue persists,')
        expect(paragraphs[3].text()).toContain('please contact us.')
        expect(wrapper.findComponent(ContactInfo).exists()).toBe(true)

        wrapper.unmount()
    })
})