import { mount } from '@vue/test-utils'
import FiledLabel from '@/components/FilingHistory/FiledLabel.vue'
import { DateTooltip } from '@/components/common'


describe('Filed Label', () => {
    it('displays no content with a null filing', () => {
        const wrapper = mount(FiledLabel, {
            props: { filing: null }
        })

        // verify content
        expect(wrapper.html()).not.toContain('Filed on')
        expect(wrapper.findComponent(DateTooltip).exists()).toBe(false)
        wrapper.unmount()
    })

    it('displays expected content with a staff type filing', () => {
        const wrapper = mount(FiledLabel, {
            props: {
                filing: {
                    isTypeStaff: true,
                    submitter: 'Submitter',
                    submittedDate: new Date('2020-05-15 12:00:00 GMT')
                }
            }
        })

        // verify content
        expect(wrapper.html().toString()).toContain('Filed on')
        expect(wrapper.html().toString()).toContain('May 15, 2020 at 5:00 am Pacific time')
        expect(wrapper.findComponent(DateTooltip).exists()).toBe(true)

        wrapper.unmount()
    })

    it('displays expected content with a non-staff type filing', () => {
        const wrapper = mount(FiledLabel, {
            props: {
                filing: {
                    isTypeStaff: false,
                    submitter: 'Submitter',
                    submittedDate: new Date('2020-05-15 12:00:00 GMT'),
                    effectiveDate: new Date('2020-05-20 12:00:00 GMT')
                }
            }
        })

        // verify content
        expect(wrapper.html().toString()).toContain('Filed on')
        expect(wrapper.html().toString()).toContain('May 15, 2020 at 5:00 am Pacific time')
        expect(wrapper.html().toString()).toContain('EFFECTIVE as of')
        expect(wrapper.html().toString()).toContain('May 20, 2020')
        expect(wrapper.findComponent(DateTooltip).exists()).toBe(true)

        wrapper.unmount()
    })
})
