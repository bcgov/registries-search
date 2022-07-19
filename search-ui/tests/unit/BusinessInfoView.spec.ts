// External
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { RouteNames } from '@/enums'
import { useEntity, useFilingHistory } from '@/composables'
import { createVueRouter } from '@/router'
import store from '@/store'
import { axios } from '@/utils'
import { BusinessInfoView } from '@/views'
// test utils
import { mockedBusinessResp, mockedFilingResp } from './utils'
import FeeServices from 'sbc-common-components/src/services/fee.services'
import { Fee } from 'sbc-common-components/src/models'


describe('BusinessInfo tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router
  sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')

  const url = 'http://legal-api-stub/'
  sessionStorage.setItem('LEGAL_API_URL', url)

  const identifier = mockedBusinessResp.identifier
  const { entity, clearEntity } = useEntity()
  const { filingHistory } = useFilingHistory()

  beforeEach(async () => {
    const mockGet = jest.spyOn(axios, 'get')
    mockGet.mockImplementation((url) => {
      switch (url) {
        case `businesses/${identifier}`:
          return Promise.resolve({ data: { business: { ...mockedBusinessResp } } })
        case `businesses/${identifier}/filings`:
          return Promise.resolve({ data: { filings: [...mockedFilingResp] } })
        case `businesses/${identifier}/documents/requests`:
          return Promise.resolve({ data: { documentAccessRequests: [] } })
      }
    })

    const addMock = jest.spyOn(FeeServices, "getFee")

    const feeArr: Fee[] = [{
      fee: 100.0,
      filingType: 'BSRCH',
      priorityFees: 0.0,
      futureEffectiveFees: 0.0,
      serviceFees: 1.50,
      total: 101.50
    },{
      fee: 25.0,
      filingType: 'CGOOD',
      priorityFees: 0.0,
      futureEffectiveFees: 0.0,
      serviceFees: 1.50,
      total: 26.50
    }]
    addMock.mockImplementation(() => Promise.resolve(feeArr))
     
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
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}`, { baseURL: url })
    // check entity was loaded
    expect(entity.bn).toBe(mockedBusinessResp.taxId)
    expect(entity.identifier).toBe(identifier)
    expect(entity.legalType).toBe(mockedBusinessResp.legalType)
    expect(entity.name).toBe(mockedBusinessResp.legalName)
    expect(entity.status).toBe(mockedBusinessResp.state)
  })
  it('loads the filing history when mounted', () => {
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}/filings`, { baseURL: url })
    // check entity was loaded
    expect(filingHistory.filings.length).toEqual(1)
  })
})
