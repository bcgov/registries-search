import { beforeEach, describe, expect, it } from 'vitest'
import { flushPromises, VueWrapper, mount } from '@vue/test-utils'
import { nextTick } from 'vue'

import BaseDatePicker from '../../../src/components/base/datePicker/Index.vue'

describe('BaseDatePicker tests', () => {
  let wrapper: VueWrapper<any>

  beforeEach(() => { wrapper = mount(BaseDatePicker) })
  afterEach(() => { wrapper.unmount() })

  it('renders DatePicker', () => {
    // test everything renders
    expect(wrapper.findComponent(BaseDatePicker).exists()).toBe(true)
    expect(wrapper.find('.bcros-date-picker').exists()).toBe(true)
    expect(wrapper.find('.bcros-date-picker__calendar').exists()).toBe(true)
    expect(wrapper.find('.bcros-date-picker__calendar__day').exists()).toBe(true)
    expect(wrapper.find('.dp__instance_calendar').exists()).toBe(true)
    expect(wrapper.vm.selectedDate).toBe(null)
    expect(wrapper.find('.dp__active_date').exists()).toBe(false)
  })
  it('selects and emits date selection', async () => {
    const days = wrapper.findAll('.bcros-date-picker__calendar__day')
    expect(days.length >= 28).toBe(true)
    expect(wrapper.vm.selectedDate).toBe(null)
    expect(wrapper.emitted('selectedDate')).toBeUndefined()
    // click day (NB: make sure it is not a day from previous/next month)
    days[9].trigger('click')
    await flushPromises()
    // should have selected / emitted
    expect(wrapper.vm.selectedDate).not.toBe(null)
    expect(wrapper.emitted('selectedDate')?.length).toBe(1)
    expect(wrapper.find('.dp__active_date').exists()).toBe(true)
  })
  it('sets default date correctly', async () => {
    const newDate = new Date('2013-04-24T12:30:00')
    wrapper = mount(BaseDatePicker, {
      props: { defaultSelectedDate: newDate }
    })
    await flushPromises()
    expect(wrapper.vm.selectedDate).toBe(newDate)
    expect(wrapper.find('.dp__active_date').exists()).toBe(true)
    expect(wrapper.find('.dp__active_date').text()).toContain(newDate.getDate())
    // changing date and clearing should put the date back to default
    const days = wrapper.findAll('.bcros-date-picker__calendar__day')
    expect(days.length >= 28).toBe(true)
    days[7].trigger('click')
    await flushPromises()
    // confirm date changed
    expect(wrapper.vm.selectedDate).not.toBe(newDate)
  })
  it('sets max/min correctly', async () => {
    // set min/max
    const minDay = 5
    const maxDay = 10
    const minDate = new Date()
    const maxDate = new Date()
    minDate.setDate(minDay)
    maxDate.setDate(maxDay)
    wrapper.setProps({ setMinDate: minDate, setMaxDate: maxDate })
    await nextTick()
    // days 1-4 and 11-* should be disabled
    const days = wrapper.findAll('.bcros-date-picker__calendar__day')
    expect(days.length >= 28).toBe(true)
    for (const i in days) {
      if (days[i].classes().includes('dp__cell_offset')) {
        // skip because it is a hidden day from the previous/next month
        continue
      }
      if (parseInt(days[i].text()) < minDay || parseInt(days[i].text()) > maxDay) {
        expect(days[i].classes()).toContain('dp__cell_disabled')
      } else {
        expect(days[i].classes()).not.toContain('dp__cell_disabled')
      }
    }
  })
  it('sets error correctly', async () => {
    // dynamically adds error
    wrapper.setProps({ error: true })
    await nextTick()
    expect(wrapper.find('.bcros-date-picker').classes()).toContain('bcros-date-picker__err')
    // dynamically clears error
    wrapper.setProps({ error: false })
    await nextTick()
    expect(wrapper.find('.bcros-date-picker').classes()).not.toContain('bcros-date-picker__err')
  })
})
