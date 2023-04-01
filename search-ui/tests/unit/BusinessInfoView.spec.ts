// External
import { flushPromises, mount, VueWrapper } from '@vue/test-utils'
import { Router } from 'vue-router'
// bcregistry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
// Local
import { AccountStatus, AccountTypes, DocumentType, FeeCodes, RouteNames, StaffRoles } from '@/enums'
import { useAuth, useEntity, useFeeCalculator, useFilingHistory } from '@/composables'
import { DocumentTypeDescriptions } from '@/resources'
import { createVueRouter } from '@/router'
import store from '@/store'
import { axios } from '@/utils'
import { BusinessInfoView } from '@/views'
// test utils
import { mockedBusinessResp, mockedFilingResp } from './utils'
import FeeServices from 'sbc-common-components/src/services/fee.services'
import { Fee } from 'sbc-common-components/src/models'

// base unchanging setup for below test suites
sessionStorage.setItem(SessionStorageKeys.KeyCloakToken, 'token')

const url = 'http://legal-api-stub/'
sessionStorage.setItem('LEGAL_API_URL', url)

const identifier = mockedBusinessResp.identifier
const { auth } = useAuth()
const { entity, clearEntity } = useEntity()
const { displayFee } = useFeeCalculator()
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
    filingType: FeeCodes.CSTAT,
    priorityFees: 0.0,
    futureEffectiveFees: 0.0,
    serviceFees: 1.50,
    total: 26.50
},{
  fee: 25.0,
  filingType: FeeCodes.LSEAL,
  priorityFees: 0.0,
  futureEffectiveFees: 0.0,
  serviceFees: 1.50,
  total: 26.50
}]

const setupBusInfoTest = (goodStanding = true) => {
  const mockGet = jest.spyOn(axios, 'get')
  if(!goodStanding){
    mockedBusinessResp.goodStanding = false
  }
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
    // check purchasable doc labels (checkboxes)
    const checkboxLabels = wrapper.findAll('.document-list__label')
    expect(checkboxLabels.length).toBe(4)
    expect(checkboxLabels[0].text()).toContain(DocumentTypeDescriptions[DocumentType.BUSINESS_SUMMARY_FILING_HISTORY])
    expect(checkboxLabels[1].text()).toContain(DocumentTypeDescriptions[DocumentType.CERTIFICATE_OF_GOOD_STANDING])
    expect(checkboxLabels[2].text()).toContain(DocumentTypeDescriptions[DocumentType.CERTIFICATE_OF_STATUS])
    expect(checkboxLabels[3].text()).toContain(DocumentTypeDescriptions[DocumentType.LETTER_UNDER_SEAL])
    // check purchasable doc fees (checkboxes)
    const checkboxFees = wrapper.findAll('.document-list__fee')
    expect(checkboxFees.length).toBe(4)
    for (const i in feeArr) {
      expect(checkboxFees[i].text()).toContain(displayFee(feeArr[i].fee, false))
    }
    // FUTURE: check fee summary
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
    auth.currentAccount = {
      accountStatus: AccountStatus.ACTIVE,
      accountType: AccountTypes.STAFF,
      id: 1,
      label: 'bcreg staff',
      productSettings: null,
      type: '',
      urlorigin: '',
      urlpath: ''
    }
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
    auth.currentAccount = {
      accountStatus: AccountStatus.ACTIVE,
      accountType: AccountTypes.SBC_STAFF,
      id: 1,
      label: 'sbc staff',
      productSettings: null,
      type: '',
      urlorigin: '',
      urlpath: ''
    }
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


describe('Display Not in Good Standing', () => {
  let wrapper: VueWrapper<any>
  let router: Router

  beforeEach(async () => {
    setupBusInfoTest(false)
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
  it('has the correct warnings in the warnings list', () => {
    expect(wrapper.vm.warnings.length).toBe(1)
    expect(wrapper.vm.warnings[0]).toBe('NOT_IN_GOOD_STANDING')     
  })
})
