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
        case `businesses/${identifier}`:
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
      bn: 'bnwjff2229',
      identifier: 'T2344567',
      incorporationDate: 'date',
      legalType: BusinessTypes.BC_LIMITED_COMPANY,
      name: 'blabla test bla',
      goodStanding: true,
      status: BusinessStatuses.ACTIVE,
      _error: null,
      _loading: false
    } as EntityI
    const clearedEntity = {
      bn: '',
      identifier: '',
      incorporationDate: '',
      legalType: null,
      name: '',
      goodStanding: true,
      status: null,
      _error: null,
      _loading: false
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
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}`, { baseURL: url })
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
    expect(axios.get).toHaveBeenCalledWith(`businesses/${identifier}`, { baseURL: url })
    // check entity was loaded
    expect(entity.bn).toBe(mockedBusinessResp.taxId)
    expect(entity.identifier).toBe(identifier)
    expect(entity.legalType).toBe(mockedBusinessResp.legalType)
    expect(entity.name).toBe(mockedBusinessResp.legalName)
    expect(entity.status).toBe(mockedBusinessResp.state)
  })
})
