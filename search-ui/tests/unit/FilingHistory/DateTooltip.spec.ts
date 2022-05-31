// External
import { mount, VueWrapper } from '@vue/test-utils'
import { DateTooltip } from '@/components/common'


describe('Date tooltip tests', () => {
    let wrapper: VueWrapper<any>


    it('displays expected content with a valid date', () => {
        // verify content
        wrapper = mount(DateTooltip, {
            props: {
                date: new Date('2020-05-15 19:00:00 GMT')
            }
        })
        // verify content
        expect(wrapper.html().toString()).toContain(wrapper.vm.dateTimeString())
        expect(wrapper.vm.dateTimeString()).toBe('May 15, 2020 at 12:00 pm Pacific time')
    })

    it('displays expected content with a null date', () => {
        // verify content
        wrapper = mount(DateTooltip, {})

        // verify content
        expect(wrapper.html().toString()).toContain(wrapper.vm.dateTimeString())
        expect(wrapper.vm.dateTimeString()).toBe('Unknown')
    })
})
