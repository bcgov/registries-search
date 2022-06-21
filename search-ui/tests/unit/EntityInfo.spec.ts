// External
import { mount, VueWrapper } from '@vue/test-utils'
// Local
import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'
import { useEntity } from '@/composables'
import { EntityInfo } from '@/components'
import { EntityI } from '@/interfaces/entity'
import { nextTick } from 'vue'


describe('Entity Info tests', () => {
  let wrapper: VueWrapper<any>

  const { clearEntity } = useEntity()

  beforeEach(async () => {
    clearEntity()
    wrapper = mount(EntityInfo, {
      shallow: true  // stubs out children components
    })
  })
  afterEach(() => {    
    jest.clearAllMocks();
  })
  it('renders EntityInfo with expected data', async () => {
    const { entity, getEntityDescription, setEntity } = useEntity()
    // displays unavailable when entity is empty
    const html = wrapper.html()
    expect(html).toContain('Name Unavailable')
    expect(html).toContain('Description Unavailable')
    // shows loader when entity is loading
    entity._loading = true
    await nextTick()
    // updates with correct data when entity is not empty
    const newEntity = {
      bn: 'bnwjff2229',
      identifier: 'T2344567',
      incorporationDate: 'date',
      legalType: BusinessTypes.BC_LIMITED_COMPANY,
      name: 'blabla test bla',
      status: BusinessStatuses.ACTIVE,
      _error: null,
      _loading: false
    } as EntityI
    setEntity(newEntity)
    await nextTick()
    entity._loading = false
    await nextTick()
    expect(entity.name).toEqual(newEntity.name)
    const htmlUpdated = wrapper.html()
    expect(htmlUpdated).toContain(newEntity.name.toUpperCase())
    expect(htmlUpdated).toContain(getEntityDescription(newEntity.legalType as CorpTypeCd))
    expect(htmlUpdated).toContain(newEntity.incorporationDate)
    expect(htmlUpdated).toContain(newEntity.identifier)
    expect(htmlUpdated).toContain(newEntity.bn)
  })
})
