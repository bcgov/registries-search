// External
import { mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import App from '@/App.vue'
import { EntityInfo } from '@/components'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { SbcHeader, SbcFooter, SbcSystemBanner } from '@/sbc-common-components'
// import vuetify from '@/plugins/vuetify'
import { useAuth } from '@/composables'
import { ProductCode, ProductStatus, RouteNames } from '@/enums'
import { SearchBusinessInfoBreadcrumb, SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/resources'
import { createVueRouter } from '@/router'
import store from '@/store'


// FUTURE: replace this with actual tests on App.vue
describe('App tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router

  beforeEach(async () => {
    // set keycloak token so it doesn't redirect
    sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
    // set auth
    const { auth } = useAuth()
    auth.tokenInitialized = true
    auth.activeProducts = [{ code: ProductCode.BUSINESS_SEARCH, subscriptionStatus: ProductStatus.ACTIVE }]
    // set router
    router = createVueRouter()
    await router.push(RouteNames.SEARCH)

    wrapper = mount(App, {
      global: {
        // plugins: [vuetify],
        plugins: [router],
        provide: {
          store: store
        },
      },
      shallow: true  // stubs out children components
    })
  })
  it('mounts App with expected child components', async () => {
    expect(wrapper.findComponent(SbcHeader).exists()).toBe(true)
    // breadcrumb will only exist with correct router meta data - should be on search + showing
    expect(wrapper.findComponent(BcrsBreadcrumb).exists()).toBe(true)
    // banner will only exist when systemMessage is not null
    expect(sessionStorage.getItem('SYSTEM_MESSAGE')).toBe(null)
    expect(wrapper.vm.systemMessage).toBe(null)
    expect(wrapper.findComponent(SbcSystemBanner).exists()).toBe(false)
    // entity info will only exist specific pages - should be on search page and hidden
    expect(wrapper.findComponent(EntityInfo).exists()).toBe(false)
    expect(wrapper.findComponent(SbcFooter).exists()).toBe(true)
  })
  it('passes correct breadcrumbs depending on route', async () => {
    const expectedSearchBreadcrumbs = [SearchHomeBreadCrumb, SearchDashboardBreadcrumb]
    const identifier = 'BC1234567'
    const businessInfoCrumb = { text: identifier, to: SearchBusinessInfoBreadcrumb.to }
    const expectedBusinessInfoBreadcrumbs = [SearchHomeBreadCrumb, SearchDashboardBreadcrumb, businessInfoCrumb]
    // currently on search route
    expect(router.currentRoute.value.name).toBe(RouteNames.SEARCH)
    expect(wrapper.findComponent(BcrsBreadcrumb).props().breadcrumbs).toEqual(expectedSearchBreadcrumbs)
    // test breadcrumbs after pushing to business info
    await router.push({name: RouteNames.BUSINESS_INFO, params: { identifier: identifier }})
    expect(router.currentRoute.value.name).toBe(RouteNames.BUSINESS_INFO)
    expect(wrapper.findComponent(BcrsBreadcrumb).props().breadcrumbs).toEqual(expectedBusinessInfoBreadcrumbs)
  })
  it('renders entity info on business info route', async () => {
    const identifier = 'BC1234567'
    await router.push({name: RouteNames.BUSINESS_INFO, params: { identifier: identifier }})
    expect(router.currentRoute.value.name).toBe(RouteNames.BUSINESS_INFO)
    expect(wrapper.findComponent(EntityInfo).exists()).toBe(true)
  })
  it('registers jest running', () => {
    expect(wrapper.vm.isJestRunning).toBe(true)
  })
})
