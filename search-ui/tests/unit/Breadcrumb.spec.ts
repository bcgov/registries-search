// Libraries
import { RouteNames } from '@/enums'
import { mount } from '@vue/test-utils'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/bcrs-common-components/resources'
import store from '@/store'


describe('Breadcrumb.vue', () => {

  const breadcrumbs : BreadcrumbIF[] = [
    {
      text: SearchHomeBreadCrumb.text,
      href: "https://yfthig-dev.web.app/dashboard"
    },
    {
      text: SearchDashboardBreadcrumb.text,
      to: { name: RouteNames.DASHBOARD }
    }
  ]

  const wrapper = mount(BcrsBreadcrumb, {
    props: { breadcrumbs },
    global: {
      provide: {
        store: store
      }
    },
    shallow: true  // stubs out children components
  })

  it('present page is dashboard so should display breadcrumb', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.v-breadcrumbs').exists()).toBe(true)
    const breadcrumbItems = wrapper.findAll('.v-breadcrumb-item')
    expect(breadcrumbItems.length).toBe(breadcrumbs.length)
    for (let i = 0; i < breadcrumbs.length; i++) {
      expect(wrapper.find('.v-breadcrumbs').html()).toContain(breadcrumbs[i].text)
    }
  })

  it('dashboard back should be redirect to search online service page', () => {
    expect(wrapper.vm.backUrl()).toBe("https://yfthig-dev.web.app/dashboard")
  })

  it('present page is dashboard so should inactive its tab', () => {
    expect(wrapper.vm.isLast(1)).toBe(true)
  })

  it('present page is search online service page so should active its tab', () => {
    expect(wrapper.vm.isLast(0)).toBe(false)
  })
})
