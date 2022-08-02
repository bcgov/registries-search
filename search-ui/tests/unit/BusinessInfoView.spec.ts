// External
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { FeeCodes, RouteNames, StaffRoles } from '@/enums'
import { useAuth, useEntity, useFilingHistory } from '@/composables'
import { createVueRouter } from '@/router'
import store from '@/store'
import { axios } from '@/utils'
import { BusinessInfoView } from '@/views'
// test utils
import { mockedBusinessResp, mockedFilingResp } from './utils'
import FeeServices from 'sbc-common-components/src/services/fee.services'
import { Fee } from 'sbc-common-components/src/models'
import { CurrentAccountI } from '@/interfaces'

// base unchanging setup for below test suites
sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')

const url = 'http://legal-api-stub/'
sessionStorage.setItem('LEGAL_API_URL', url)

const identifier = mockedBusinessResp.identifier
const { auth } = useAuth()
const { entity, clearEntity } = useEntity()
const { filingHistory } = useFilingHistory()

const feeArr: Fee[] = [{
    fee: 100.0,
    filingType: FeeCodes.BSRCH,
    priorityFees: 0.0,
    futureEffectiveFees: 0.0,
    serviceFees: 1.50,
    total: 101.50
  },{
    fee: 25.0,
    filingType: FeeCodes.CGOOD,
    priorityFees: 0.0,
    futureEffectiveFees: 0.0,
    serviceFees: 1.50,
    total: 26.50
  },{
    fee: 25.0,
    filingType: 'CSTAT',
    priorityFees: 0.0,
    futureEffectiveFees: 0.0,
    serviceFees: 1.50,
    total: 26.50
}]

const setupBusInfoTest = () => {
  const mockGet = jest.spyOn(axios, 'get')
  mockGet.mockImplementation((url) => {
    switch (url) {
      case `businesses/${identifier}`:
        return Promise.resolve({ data: { business: { ...mockedBusinessResp } } })
      case `businesses/${identifier}/filings`:
        return Promise.resolve({ data: { filings: [...mockedFilingResp] } })
    }
  })

  const addMock = jest.spyOn(FeeServices, "getFee")
  addMock.mockImplementation(() => Promise.resolve(feeArr))

  clearEntity()
}

describe('BusinessInfo tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router

  beforeEach(async () => {
    setupBusInfoTest()
    router = createVueRouter()
    await router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
    wrapper = mount(BusinessInfoView, {
      props: { identifier: identifier, appReady: true },
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
    jest.clearAllMocks()
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
  it('sets the fee codes + pre service fee properly for a non staff user', () => {
    expect(wrapper.vm.bsrchCode).toBe(FeeCodes.BSRCH)
    expect(wrapper.vm.feePreSelectItem.serviceFee).toBe(1.5)
  })
})

describe('Registry Staff BusinessInfo tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router

  beforeEach(async () => {
    setupBusInfoTest()
    auth.staffRoles.push(StaffRoles.STAFF)
    router = createVueRouter()
    await router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
    wrapper = mount(BusinessInfoView, {
      props: { identifier: identifier, appReady: true },
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
    jest.clearAllMocks()
    auth.staffRoles = []
  })
  it('sets the fee codes + pre service fee properly for bc reg staff', () => {
    expect(wrapper.vm.bsrchCode).toBe(FeeCodes.SBSRCH)
    expect(wrapper.vm.feePreSelectItem.serviceFee).toBe(0)
  })
})

describe('SBC Staff BusinessInfo tests', () => {
  let wrapper: VueWrapper<any>
  let router: Router

  beforeEach(async () => {
    setupBusInfoTest()
    auth.staffRoles.push(StaffRoles.SBC)
    router = createVueRouter()
    await router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
    wrapper = mount(BusinessInfoView, {
      props: { identifier: identifier, appReady: true },
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
    jest.clearAllMocks()
    auth.staffRoles = []
  })
  it('sets the fee codes + pre service fee properly for bc reg staff', () => {
    expect(wrapper.vm.bsrchCode).toBe(FeeCodes.SBSRCH)
    expect(wrapper.vm.feePreSelectItem.serviceFee).toBe(0)
  })
})
