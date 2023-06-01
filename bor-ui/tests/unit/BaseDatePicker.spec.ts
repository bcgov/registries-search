import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
// local
import { BaseDatePicker } from '@/components'
import { nextTick } from 'vue'

describe('BaseDatePicker tests', () => {
  let wrapper: VueWrapper<any>

  beforeEach(async () => {
    wrapper = mount(BaseDatePicker)
  })
  it('renders BaseDatePicker', () => {
    // test everything renders
    expect(wrapper.findComponent(BaseDatePicker).exists()).toBe(true)
    expect(wrapper.find('.base-date-picker').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__header').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__header__year').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__header__year').text()).toBe(`${(new Date()).getFullYear()}`)
    expect(wrapper.find('.base-date-picker__header__date').exists()).toBe(false)
    expect(wrapper.find('.base-date-picker__month-year').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__month-year__prev-btn').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__month-year__date-btn').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__month-year__next-btn').exists()).toBe(true)
    // month / year selections are not open
    expect(wrapper.find('.base-date-picker__select__year').exists()).toBe(false)
    expect(wrapper.find('.base-date-picker__select__month').exists()).toBe(false)
  })

  it('allows year selection from header', async () => {
    wrapper.find('.base-date-picker__header__year').trigger('click')
    await flushPromises()
    expect(wrapper.find('.base-date-picker__select__year').exists()).toBe(true)
    // list of buttons is there
    const year_btn_list = wrapper.findAll('.base-date-picker__select__year__btn')
    expect(year_btn_list.length).toBe(201)
    // default selection is current year
    expect(wrapper.find('.base-date-picker__select__year__btn.selected').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__select__year__btn.selected').text()).toBe(`${(new Date()).getFullYear()}`)
    // click different year
    year_btn_list[0].trigger('click')
    await flushPromises()
    expect(wrapper.find('.base-date-picker__select__year').exists()).toBe(false)
    expect(wrapper.find('.base-date-picker__header__year').text()).toBe(`${year_btn_list[0].text()}`)
    expect(wrapper.find('.base-date-picker__month-year').text()).toContain(`${year_btn_list[0].text()}`)
  })

  it('allows month/year prev/next/selection from month-year menu', async () => {
    const startingMonth = wrapper.vm.selectedMonth
    // click prev
    wrapper.find('.base-date-picker__month-year__prev-btn').trigger('click')
    await flushPromises()
    expect(wrapper.vm.selectedMonth).not.toBe(startingMonth)
    // click next
    wrapper.find('.base-date-picker__month-year__next-btn').trigger('click')
    await flushPromises()
    expect(wrapper.vm.selectedMonth).toBe(startingMonth)
    // click date
    wrapper.find('.base-date-picker__month-year__date-btn').trigger('click')
    await flushPromises()
    // month menu should be open
    expect(wrapper.find('.base-date-picker__select__month').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__select__year').exists()).toBe(false)
    const monthBtns = wrapper.findAll('.base-date-picker__select__month__btn')
    expect(monthBtns.length).toBe(12)
    expect(monthBtns[startingMonth].classes()).toContain('selected')
    const selectedMonth = startingMonth < 11 ? 11 : 3
    monthBtns[selectedMonth].trigger('click')
    await flushPromises()
    expect(wrapper.vm.selectedMonth).toBe(selectedMonth)
    // year picker should be open
    expect(wrapper.find('.base-date-picker__select__year').exists()).toBe(true)
    expect(wrapper.find('.base-date-picker__select__month').exists()).toBe(false)
    const year_btn_list = wrapper.findAll('.base-date-picker__select__year__btn')
    expect(year_btn_list.length).toBe(201)
    // select new year
    year_btn_list[0].trigger('click')
    await flushPromises()
    // menus should be closed, selected year/month should be shown
    expect(wrapper.find('.base-date-picker__select__year').exists()).toBe(false)
    expect(wrapper.find('.base-date-picker__select__month').exists()).toBe(false)
    expect(wrapper.find('.base-date-picker__month-year__date-btn').text()).toContain(monthBtns[selectedMonth].text())
    expect(wrapper.find('.base-date-picker__month-year__date-btn').text()).toContain(year_btn_list[0].text())
  })

  it('selects and emits date and resets', async () => {
    const days = wrapper.findAll('.base-date-picker__calendar__day')
    expect(days.length >= 30).toBe(true)
    expect(wrapper.vm.selectedDate).toBe(null)
    expect(wrapper.emitted('selectedDate')).toBeUndefined()
    // click day (NB: make sure it is not a day from previous/next month)
    days[9].trigger('click')
    await flushPromises()
    // should have selected / emitted
    expect(wrapper.vm.selectedDate).not.toBe(null)
    expect(wrapper.emitted('selectedDate').length).toBe(1)
    // reset
    wrapper.setProps({ resetTrigger: true })
    await flushPromises()
    // selected date should be null / emitted
    expect(wrapper.vm.selectedDate).toBe(null)
    expect(wrapper.emitted('selectedDate').length).toBe(2)
    expect(wrapper.emitted('selectedDate')[1]).toEqual([null])
  })

  it('sets defaults correctly', async () => {
    const newDate = new Date('2013-04-24T12:30:00')
    wrapper = mount(BaseDatePicker, {
      props: {
        defaultSelectedDate: newDate
      }
    })
    await flushPromises()
    expect(wrapper.vm.selectedDate).toBe(newDate)
    expect(wrapper.vm.selectedMonth).toBe(newDate.getMonth())
    expect(wrapper.vm.selectedYear).toBe(newDate.getFullYear())
    expect(wrapper.find('.base-date-picker__header__year').text()).toBe(`${newDate.getFullYear()}`)
    expect(wrapper.find('.base-date-picker__header__date').exists()).toBe(true)
    // changing date and clearing should put the date back to default
    const days = wrapper.findAll('.base-date-picker__calendar__day')
    expect(days.length >= 30).toBe(true)
    days[1].trigger('click')
    await flushPromises()
    // confirm date changed
    expect(wrapper.vm.selectedDate).not.toBe(newDate)
    // reset
    wrapper.setProps({ resetTrigger: true })
    await flushPromises()
    // check it went back to original defaults
    expect(wrapper.vm.selectedDate).toBe(newDate)
    expect(wrapper.vm.selectedMonth).toBe(newDate.getMonth())
    expect(wrapper.vm.selectedYear).toBe(newDate.getFullYear())
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
    const days = wrapper.findAll('.base-date-picker__calendar__day')
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
    expect(wrapper.find('.base-date-picker').classes()).toContain('base-date-picker__err')
    // dynamically clears error
    wrapper.setProps({ error: false })
    await nextTick()
    expect(wrapper.find('.base-date-picker').classes()).not.toContain('base-date-picker__err')
  })
})