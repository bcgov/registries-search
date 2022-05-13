// Libraries
import { RouteNames } from '@/enums'
import { mount } from '@vue/test-utils'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { SearchDashboardBreadcrumb, SearchSIGNINBreadcrumb } from '@/bcrs-common-components/resources'
import store from '@/store'


describe('Breadcrumb.vue', () => {

  const breadcrumbs : BreadcrumbIF[] = [
    {
      text: SearchSIGNINBreadcrumb.text,
      to: { name: RouteNames.SIGN_IN }
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
      },
      mocks: {
        $route: {
          name: RouteNames.DASHBOARD
        }
      }
    },
    shallow: true  // stubs out children components
  })

  it('present page is dashboard so should display breadcrumb', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('dashboard back should be redirect to sign in', () => {
    expect(wrapper.vm.backUrl()).toBe(RouteNames.SIGN_IN)
  })

  it('present page is dashboard so should in active this tab', () => {
    expect(wrapper.vm.isActiveCrumb({ text: SearchDashboardBreadcrumb.text , to: { name: RouteNames.DASHBOARD } })).toBe(false)
  })
})
