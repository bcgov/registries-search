import { mount } from '@vue/test-utils'
import StaffFiling from '@/components/FilingHistory/StaffFiling.vue'


describe('Staff Filing', () => {
    it('displays no content with a null filing', () => {
        const wrapper = mount(StaffFiling, {
            props: { filing: null }
        })

        // verify content
        const paras = wrapper.findAll('.staff-filing-details > p')
        expect(paras.length).toEqual(0)
        wrapper.unmount()
    })

    it('displays expected content with all data', () => {
        const wrapper = mount(StaffFiling, {
            props: {
                filing: {
                    notationOrOrder: 'Notation Or Order',
                    fileNumber: '1234',
                    planOfArrangement: 'Plan Of Arrangement'
                }
            }
        })

        // verify content

        const paras = wrapper.findAll('.staff-filing-details > p')
        expect(paras[0].text()).toBe('Notation Or Order')
        expect(paras[1].text()).toBe('Court Order Number: 1234')
        expect(paras[2].text()).toBe('Plan Of Arrangement')

        wrapper.unmount()
    })
})
