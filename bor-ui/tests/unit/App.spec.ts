// External
import { Router } from 'vue-router'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import App from '@/App.vue'
import { BcrsBreadcrumb } from '@/bcrs-shared-components'
import { SbcHeader, SbcFooter, SbcSystemBanner } from '@/sbc-common-components'
// import vuetify from '@/plugins/vuetify'
import { useAuth, _readOnly } from '@/composables'
import { ErrorCategory, ErrorCode, RouteName } from '@/enums'
import { SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/resources'
import { DefaultError } from '@/resources/error-dialog-options'
import { createVueRouter } from '@/router'
import store from '@/store'


// FUTURE: replace this with actual tests on App.vue
describe('App tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router
  const { auth } = useAuth()

  beforeEach(async () => {
    // set keycloak token so it doesn't redirect
    sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')
    // set auth
    _readOnly.tokenInitialized = true
    // set router
    router = createVueRouter()
    await router.push(RouteName.SEARCH)

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
    expect(wrapper.findComponent(SbcFooter).exists()).toBe(true)
  })
  it('passes correct breadcrumbs depending on route', async () => {
    const expectedSearchBreadcrumbs = [SearchHomeBreadCrumb, SearchDashboardBreadcrumb]
    // currently on search route
    expect(router.currentRoute.value.name).toBe(RouteName.SEARCH)
    expect(wrapper.findComponent(BcrsBreadcrumb).props().breadcrumbs).toEqual(expectedSearchBreadcrumbs)
  })
  it('registers jest running', () => {
    expect(wrapper.vm.isJestRunning).toBe(true)
  })
  it('triggers auth error dialog', async () => {
    // confirm in an error free state
    expect(auth._error).toBe(null)
    expect(wrapper.vm.errorDisplay).toBe(false)
    expect(wrapper.vm.errorContactInfo).toBe(false)
    expect(wrapper.vm.errorInfo).toBe(null)
    // set error
    _readOnly.error = {
      category: ErrorCategory.ACCOUNT_SETTINGS,
      message: 'Error getting/setting current account.',
      statusCode: null,
      type: ErrorCode.ACCOUNT_SETUP_ERROR
    }
    await flushPromises()
    // check error dialog values have updated
    expect(wrapper.vm.errorDisplay).toBe(true)
    expect(wrapper.vm.errorContactInfo).toBe(true)
    expect(wrapper.vm.errorInfo).toEqual(DefaultError)
  })
})