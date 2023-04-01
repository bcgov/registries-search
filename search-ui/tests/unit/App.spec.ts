// External
import { Router } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import App from '@/App.vue'
import { EntityInfo } from '@/components'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { SbcHeader, SbcFooter } from '@/sbc-common-components'
// import vuetify from '@/plugins/vuetify'
import { useAuth, useDocumentAccessRequest, useEntity } from '@/composables'
import { ErrorCategories, ErrorCodes, ProductCode, ProductStatus, RouteNames } from '@/enums'
import { SearchBusinessInfoBreadcrumb, SearchDashboardBreadcrumb, SearchHomeBreadCrumb } from '@/resources'
import { DefaultError, EntityLoadError, PayDefaultError } from '@/resources/error-dialog-options'
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
  it('triggers auth error dialog', async () => {
    // confirm in an error free state
    expect(auth._error).toBe(null)
    expect(wrapper.vm.errorDisplay).toBe(false)
    expect(wrapper.vm.errorContactInfo).toBe(false)
    expect(wrapper.vm.errorInfo).toBe(null)
    // set error
    auth._error = {
      category: ErrorCategories.ACCOUNT_SETTINGS,
      message: 'Error getting/setting current account.',
      statusCode: null,
      type: ErrorCodes.ACCOUNT_SETUP_ERROR
    }
    await flushPromises()
    // check error dialog values have updated
    expect(wrapper.vm.errorDisplay).toBe(true)
    expect(wrapper.vm.errorContactInfo).toBe(true)
    expect(wrapper.vm.errorInfo).toEqual(DefaultError)
  })

  it('triggers document access request error dialog', async () => {
    // confirm in an error free state
    const { documentAccessRequest } = useDocumentAccessRequest()
    expect(documentAccessRequest._error).toBe(null)
    expect(wrapper.vm.errorDisplay).toBe(false)
    expect(wrapper.vm.errorContactInfo).toBe(false)
    expect(wrapper.vm.errorInfo).toBe(null)
    // set error
    documentAccessRequest._error = {
      category: ErrorCategories.DOCUMENT_ACCESS_REQUEST_CREATE,
      detail: 'pay default error',
      message: 'not used',
      statusCode: StatusCodes.PAYMENT_REQUIRED,
      type: null
    }
    await flushPromises()
    // check error dialog values have updated
    expect(wrapper.vm.errorDisplay).toBe(true)
    expect(wrapper.vm.errorContactInfo).toBe(true)
    expect(wrapper.vm.errorInfo).toEqual(PayDefaultError)
  })

  it('triggers entity error dialog', async () => {
    // confirm in an error free state
    const { entity } = useEntity()
    expect(entity._error).toBe(null)
    expect(wrapper.vm.errorDisplay).toBe(false)
    expect(wrapper.vm.errorContactInfo).toBe(false)
    expect(wrapper.vm.errorInfo).toBe(null)
    // set error
    entity._error = {
      category: ErrorCategories.ENTITY_BASIC,
      detail: 'not used',
      message: 'not used',
      statusCode: null,
      type: null
    }
    await flushPromises()
    // check error dialog values have updated
    expect(wrapper.vm.errorDisplay).toBe(true)
    expect(wrapper.vm.errorContactInfo).toBe(true)
    expect(wrapper.vm.errorInfo).toEqual(EntityLoadError)
  })
})
