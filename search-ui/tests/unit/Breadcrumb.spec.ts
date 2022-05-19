// external
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// local
import { RouteNames } from '@/enums'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/resources'
import { createVueRouter } from '@/router'


describe('Breadcrumb.vue', () => {

  const breadcrumbs : BreadcrumbIF[] = [
    { text: SearchHomeBreadCrumb.text, href: "http://mock-home" },
    { text: SearchDashboardBreadcrumb.text, to: { name: RouteNames.SEARCH }},
    { text: 'active breadcrumb', to: { name: RouteNames.BUSINESS_INFO }}
  ]

  const wrapper = mount(BcrsBreadcrumb, {
    props: { breadcrumbs },
    shallow: true  // stubs out children components
  })

  it('displays breadcrumbs', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.breadcrumb-col').exists()).toBe(true)
    const breadcrumbItems = wrapper.findAll('.v-breadcrumb-item')
    expect(breadcrumbItems.length).toBe(breadcrumbs.length)
    for (let i = 0; i < breadcrumbs.length; i++) {
      expect(wrapper.find('.breadcrumb-col').html()).toContain(breadcrumbs[i].text)
    }
  })
  it('gives expected isLast value', () => {
    for (let i=0; i<breadcrumbs.length; i++) {
      if (i < breadcrumbs.length-1) expect(wrapper.vm.isLast(i)).toBe(false)
      else expect(wrapper.vm.isLast(i)).toBe(true)
    }
  })
})

describe('Breadcrumb.vue router tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router

  const location = window.location

  const breadcrumbs : BreadcrumbIF[] = [
    { text: SearchHomeBreadCrumb.text, href: "http://mock-home" },
    { text: SearchDashboardBreadcrumb.text, to: { name: RouteNames.SEARCH }},
    { text: '123', to: { name: RouteNames.BUSINESS_INFO }}
  ]

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    // set token so that router does not redirect to auth
    sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
    router = createVueRouter()
    router.push({name: RouteNames.SEARCH})
    await router.isReady()

    wrapper = mount(BcrsBreadcrumb, {
      props: { breadcrumbs: [breadcrumbs[0], breadcrumbs[1]] },
      global: { plugins: [router], },
      shallow: true  // stubs out children components
    })
  })
  afterEach(() => {
    window.location = location
  })

  it('renders with router initialized at search', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.breadcrumb-col').exists()).toBe(true)
    expect(router.currentRoute.value.name).toBe(RouteNames.SEARCH)
  })
  it('goes to mocked href of when clicking back', async () => {
    await wrapper.vm.back()
    expect(window.location.assign).toHaveBeenCalledWith(breadcrumbs[0].href)
    // test click from UI
    const backBtn = wrapper.find('#breadcrumb-back-btn')
    await backBtn.trigger('click')
    await flushPromises()
    expect(window.location.assign).toHaveBeenCalledWith(breadcrumbs[0].href)
  })
  it('renders properly when router is pushed to business info', async () => {
    await router.push({name: RouteNames.BUSINESS_INFO, params: { identifier: '123' }})
    await wrapper.setProps({breadcrumbs: breadcrumbs})
    for (let i = 0; i < breadcrumbs.length; i++) {
      const crumb = wrapper.findAll('.breadcrumb-text')[i]
      expect(crumb.text()).toBe(breadcrumbs[i].text)
    }
    // simulate click
    const crumb2 = wrapper.findAll('.breadcrumb-text')[1]
    await crumb2.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe(breadcrumbs[1].to.name)
    // put router back to business info
    await router.push({name: RouteNames.BUSINESS_INFO, params: { identifier: '123' }})
    expect(router.currentRoute.value.name).toBe(RouteNames.BUSINESS_INFO)
    // simulate back btn
    const backBtn = wrapper.find('#breadcrumb-back-btn')
    await backBtn.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe(breadcrumbs[1].to.name)
  })
})
