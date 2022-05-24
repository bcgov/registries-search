// External
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { RouteNames } from '@/enums'
import { useEntity } from '@/composables'
import { createVueRouter } from '@/router'
import store from '@/store'
import { axios } from '@/utils'
import { BusinessInfoView } from '@/views'
// test utils
import { mockedBusinessResp } from './utils'


describe('BusinessInfo tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router
  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')

  const url = 'http://legal-api-stub'
  sessionStorage.setItem('LEGAL_API_URL', url)

  const identifier = mockedBusinessResp.identifier
  const { entity, clearEntity } = useEntity()

  beforeEach(async () => {
    const mockGet = jest.spyOn(axios, 'get')
    mockGet.mockImplementation((url) => {
      switch (url) {
        case `businesses/${identifier}`:
          return Promise.resolve({ data: { business: { ...mockedBusinessResp } } })
        // FUTURE: add case for filing history
      }
    })
    clearEntity()
    router = createVueRouter()
    await router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
    wrapper = mount(BusinessInfoView, {
      props: { identifier: identifier },
      global: {
        plugins: [router],
        provide: { store: store },
      },
      shallow: true  // stubs out children components
    })
    // await api calls to resolve
    await flushPromises()
  })
  afterEach(() => {    
    jest.clearAllMocks();
  })
  it('renders BusinessInfo with expected child components', () => {
    // check headers are there
    expect(wrapper.html()).toContain('How to Access Business Documents')
    expect(wrapper.html()).toContain('Available Documents to Download:')
    // FUTURE: check fee summary / checkbox / filing history comp render
  })
  it('loads the entity of the given identifier when mounted', () => {
    // check call was made
    expect(axios.get).toBeCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}`, { baseURL: url })
    // check entity was loaded
    expect(entity.bn).toBe(mockedBusinessResp.taxId)
    expect(entity.identifier).toBe(identifier)
    expect(entity.legalType).toBe(mockedBusinessResp.legalType)
    expect(entity.name).toBe(mockedBusinessResp.legalName)
    expect(entity.status).toBe(mockedBusinessResp.state)
  })
})
