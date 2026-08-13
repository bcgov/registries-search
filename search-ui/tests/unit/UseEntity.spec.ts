// Local
import { useEntity } from '@/composables'
import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'
import { EntityI } from '@/interfaces/entity'
import { axios } from '@/utils'
// test utils
import { mockedBusinessResp } from './utils'


describe('Entity Factory tests', () => {
  const identifier = mockedBusinessResp.identifier
  const { entity, clearEntity } = useEntity()

  beforeEach(async () => {
    // mocks
    const mockGet = jest.spyOn(axios, 'get')
    mockGet.mockImplementation((url) => {
      switch (url) {
        case `businesses/${identifier}?slim=true`:
          return Promise.resolve({ data: { business: { ...mockedBusinessResp } } })
        // FUTURE: add case for filing history
      }
    })
    // reset entity
    clearEntity()
  })
  afterEach(() => {    
    jest.clearAllMocks();
  })
  it('sets and clears entity properly', () => {
    // setup
    const { setEntity } = useEntity()
    const newEntity = {
      amalgamatedInto: null,
      bn: 'bnwjff2229',
      identifier: 'T2344567',
      incorporationDate: 'date',
      legalType: BusinessTypes.BC_LIMITED_COMPANY,
      name: 'blabla test bla',
      goodStanding: true,
      status: BusinessStatuses.ACTIVE,
      stateFiling: '',
      _error: null,
      _loading: false,
      _stateFilingInfo: null
    } as EntityI
    const clearedEntity = {
      amalgamatedInto: null,
      bn: '',
      identifier: '',
      incorporationDate: '',
      legalType: null,
      name: '',
      goodStanding: true,
      inDissolution: false,
      status: null,
      stateFiling: '',
      _error: null,
      _loading: false,
      _stateFilingInfo: null
    } as EntityI
    expect(entity).not.toEqual(newEntity)
    // set entity
    setEntity(newEntity)
    expect(entity).toEqual(newEntity)
    // clear entity
    clearEntity()
    expect(entity).toEqual(clearedEntity)
  })
  it('gets all descriptions of business types', () => {
    const { getEntityDescription } = useEntity()
    // returns '' if no description
    expect(getEntityDescription('fakeCorpType' as CorpTypeCd)).toBe('')
    for (const status in Object.values(BusinessStatuses)) {
      expect(getEntityDescription(status as CorpTypeCd)).toBe('')
    }
  })
  it('gets new entity info properly', async () => {
    // setup
    const url = 'http://legal-api-stub'
    sessionStorage.setItem('LEGAL_API_URL', url)
    expect(axios.get).toBeCalledTimes(0)
    const { getEntityInfo } = useEntity()
    // test fn
    const newEntity = await getEntityInfo(identifier)
    // check call was made
    expect(axios.get).toBeCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}?slim=true`, { baseURL: url })
    // check entity was loaded
    expect(newEntity.bn).toBe(mockedBusinessResp.taxId)
    expect(newEntity.identifier).toBe(identifier)
    expect(newEntity.legalType).toBe(mockedBusinessResp.legalType)
    expect(newEntity.name).toBe(mockedBusinessResp.legalName)
    expect(newEntity.status).toBe(mockedBusinessResp.state)
  })
  it('loads new entity info properly', async () => {
    // setup
    const url = 'http://legal-api-stub'
    sessionStorage.setItem('LEGAL_API_URL', url)
    expect(axios.get).toBeCalledTimes(0)
    const { loadEntity } = useEntity()
    // test fn
    await loadEntity(identifier)
    // check call was made
    expect(axios.get).toBeCalledTimes(1)
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}?slim=true`, { baseURL: url })
    // check entity was loaded
    expect(entity.bn).toBe(mockedBusinessResp.taxId)
    expect(entity.identifier).toBe(identifier)
    expect(entity.legalType).toBe(mockedBusinessResp.legalType)
    expect(entity.name).toBe(mockedBusinessResp.legalName)
    expect(entity.status).toBe(mockedBusinessResp.state)
  })
  it('loads the state filing info for a historical entity', async () => {
    // setup
    const url = 'http://legal-api-stub'
    sessionStorage.setItem('LEGAL_API_URL', url)
    const stateFilingUrl = `${url}/businesses/${identifier}/filings/112233`
    const mockGet = jest.spyOn(axios, 'get')
    mockGet.mockImplementation((getUrl) => {
      switch (getUrl) {
        case `businesses/${identifier}?slim=true`:
          return Promise.resolve({
            data: {
              business: {
                ...mockedBusinessResp,
                state: BusinessStatuses.HISTORICAL,
                stateFiling: stateFilingUrl
              }
            }
          })
        case `${stateFilingUrl}?public=true`:
          return Promise.resolve({
            data: {
              filing: {
                header: { name: 'dissolution', effectiveDate: '2024-03-15T18:30:00+00:00' },
                dissolution: { type: 'voluntary' }
              }
            }
          })
      }
    })
    const { loadEntity } = useEntity()
    // test fn
    await loadEntity(identifier)
    // check both calls were made and state filing info was set
    expect(axios.get).toBeCalledTimes(2)
    expect(axios.get).toHaveBeenCalledWith(`${stateFilingUrl}?public=true`)
    expect(entity._stateFilingInfo?.header?.name).toBe('dissolution')
  })
  it('sets the historical reason for an amalgamated entity', () => {
    const { historicalReason, setEntity } = useEntity()
    setEntity({
      ...entity,
      status: BusinessStatuses.HISTORICAL,
      amalgamatedInto: {
        amalgamationDate: '2024-03-15T18:30:00+00:00',
        amalgamationType: 'regular',
        courtApproval: false,
        identifier: 'BC7654321',
        legalName: 'new amalgamated business'
      }
    } as EntityI)
    expect(historicalReason.value).toBe('Amalgamation – March 15, 2024 – BC7654321')
  })
  it('sets the historical reason based on the state filing', () => {
    const { historicalReason, setEntity } = useEntity()
    const baseEntity = {
      ...entity,
      legalType: BusinessTypes.BC_LIMITED_COMPANY,
      status: BusinessStatuses.HISTORICAL,
      stateFiling: 'http://fake-url'
    }
    // voluntary dissolution
    setEntity({
      ...baseEntity,
      _stateFilingInfo: {
        header: { name: 'dissolution', effectiveDate: '2024-03-15T18:30:00+00:00' },
        dissolution: { type: 'voluntary' }
      }
    } as EntityI)
    expect(historicalReason.value).toBe('Voluntary Dissolution – March 15, 2024')
    // involuntary dissolution
    setEntity({
      ...baseEntity,
      _stateFilingInfo: {
        header: { name: 'dissolution', effectiveDate: '2024-03-15T18:30:00+00:00' },
        dissolution: { type: 'involuntary' }
      }
    } as EntityI)
    expect(historicalReason.value).toBe('Involuntary Dissolution – March 15, 2024')
    // put back off
    setEntity({
      ...baseEntity,
      _stateFilingInfo: {
        header: { name: 'putBackOff', effectiveDate: '2024-03-15T18:30:00+00:00' },
        putBackOff: { reason: 'Limited Restoration', expiryDate: '2024-03-15' }
      }
    } as EntityI)
    expect(historicalReason.value).toBe('Limited Restoration on March 15, 2024')
    // continuation out
    setEntity({
      ...baseEntity,
      _stateFilingInfo: {
        header: { name: 'continuationOut', effectiveDate: '2024-03-15T18:30:00+00:00' },
        continuationOut: {}
      }
    } as EntityI)
    expect(historicalReason.value).toBe('Continuation Out – March 15, 2024 at 11:30 am Pacific time')
    // no state filing info
    setEntity({ ...baseEntity, _stateFilingInfo: null } as EntityI)
    expect(historicalReason.value).toBe('')
    // not historical
    setEntity({ ...baseEntity, status: BusinessStatuses.ACTIVE } as EntityI)
    expect(historicalReason.value).toBe('')
  })
})
