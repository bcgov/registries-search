import { reactive } from 'vue'
// Local
import { CorpTypeCd } from '@/enums'
import { getEntity } from '@/requests'
import { CorpInfoArray } from '@/resources'
import { EntityI } from '@/interfaces/entity'

const entity = reactive({
  bn: '',
  identifier: '',
  incorporationDate: '',
  legalType: null,
  name: '',
  state: null,
  _error: null,
  _loading: false,
} as EntityI)

export const useEntity = () => {
  // functions, etc. to manage the entity state
  const clearEntity = () => {
    entity.bn = ''
    entity.identifier = ''
    entity.incorporationDate = ''
    entity.legalType = null
    entity.name = ''
    entity.state = null
    entity._error = null
    entity._loading = false
  }
  const loadEntity = async (identifier: string) => {
    entity._loading = true
    clearEntity()
    const entityInfo = await getEntityInfo(identifier)
    if (entityInfo) {
      setEntity(entityInfo)
    }
    entity._loading = false
  }
  const getEntityDescription = (entityType: CorpTypeCd) => {
    const item = CorpInfoArray.find(obj => (entityType === obj.corpTypeCd))
    return (item && item.fullDesc) || ''
  }
  const getEntityInfo = async (identifier: string) => {
    // call legal api for entity data
    const entityInfo = await getEntity(identifier)
    if (entityInfo.error) {
      entity._error = entityInfo.error
      return null
    }
    return entityInfo
  }
  const setEntity = (newEntity: EntityI) => {
    entity.bn = newEntity.bn || ''
    entity.identifier = newEntity.identifier
    entity.incorporationDate = newEntity.incorporationDate
    entity.legalType = newEntity.legalType
    entity.name = newEntity.name
    entity.state = newEntity.state
  }
  return {
    entity,
    clearEntity,
    getEntityDescription,
    getEntityInfo,
    loadEntity,
    setEntity
  }
}