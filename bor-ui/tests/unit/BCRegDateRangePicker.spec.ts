// external
import { VueWrapper, flushPromises, mount } from '@vue/test-utils'
// internal
import { BCRegDateRangePicker, BaseDatePicker } from '@/components'

describe('BC Reg Date Range Picker tests', () => {
  let wrapper: VueWrapper<any>

  it('renders and displays the date range picker', async () => {
    wrapper = mount(BCRegDateRangePicker)
    expect(wrapper.findComponent(BCRegDateRangePicker).exists()).toBe(true)
    // headers
    expect(wrapper.findAll('.date-selection__heading').length).toBe(2)
    expect(wrapper.findAll('.date-selection__heading')[0].text()).toBe('Select Start Date:')
    expect(wrapper.findAll('.date-selection__heading')[1].text()).toBe('Select End Date:')
    // calendars
    expect(wrapper.findAllComponents(BaseDatePicker).length).toBe(2)
    // buttons
    expect(wrapper.findAll('.date-selection-btn').length).toBe(2)
    expect(wrapper.findAll('.date-selection-btn')[0].text()).toBe('OK')
    expect(wrapper.findAll('.date-selection-btn')[1].text()).toBe('Cancel')
    // no error validations
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(wrapper.findAll('.date-selection__heading.picker-err').length).toBe(0)
    expect(wrapper.findAllComponents(BaseDatePicker)[0].vm.$props.error).toBe(false)
    expect(wrapper.findAllComponents(BaseDatePicker)[1].vm.$props.error).toBe(false)
  })

  it('Validates and submits the date range selections', async () => {
    wrapper = mount(BCRegDateRangePicker)
    // click okay + test validation
    let submitButtons = wrapper.findAll('.date-selection-btn')
    submitButtons[0].trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(true)
    expect(wrapper.emitted('submit')).toBeUndefined()
    // click cancel + test validation reset / emit nulls
    submitButtons[1].trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(wrapper.emitted('submit').length).toBe(1)
    expect(wrapper.emitted('submit')[0]).toEqual([{ endDate: null, startDate: null }])
    // set start date only + test validation
    const startDate = new Date('2021-10-22')
    wrapper = mount(BCRegDateRangePicker, { props: { defaultStartDate: startDate } })
    submitButtons = wrapper.findAll('.date-selection-btn')
    expect(wrapper.vm.startDate).toBe(startDate)
    // // should still trigger validation err
    submitButtons[0].trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(true)
    // end date should have error validation
    expect(wrapper.findAll('.date-selection__heading.picker-err').length).toBe(1)
    expect(wrapper.findAll('.date-selection__heading.picker-err')[0].text()).toBe('Select End Date:')
    expect(wrapper.findAllComponents(BaseDatePicker)[1].vm.$props.error).toBe(true)
    // check no event was triggered
    expect(wrapper.emitted('submit')).toBeUndefined()
    // select end date and submit should emit values
    const endDate = new Date('2021-10-23')
    wrapper = mount(BCRegDateRangePicker, { props: { defaultStartDate: startDate, defaultEndDate: endDate } })
    submitButtons = wrapper.findAll('.date-selection-btn')
    expect(wrapper.vm.startDate).toBe(startDate)
    expect(wrapper.vm.endDate).toBe(endDate)
    submitButtons[0].trigger('click')
    await flushPromises()
    expect(wrapper.vm.datePickerErr).toBe(false)
    expect(wrapper.emitted('submit').length).toBe(1)
    expect(wrapper.emitted('submit')[0]).toEqual([{ startDate: startDate, endDate: endDate }])
  })
})
