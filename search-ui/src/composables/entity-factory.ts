import { computed, reactive } from 'vue'
// Local
import { BusinessStatuses, BusinessTypes, CorpTypeCd, FilingNames, FilingSubTypes, FilingTypes } from '@/enums'
import { getEntity, getStateFilingInfo } from '@/requests'
import { CorpInfoArray } from '@/resources'
import { EntityI } from '@/interfaces/entity'
import {
  apiToDate, dateToPacificDate, dateToPacificDateTime, filingTypeToName, yyyyMmDdToDate
} from '@/utils'

const entity = reactive({
  amalgamatedInto: null,
  bn: '',
  identifier: '',
  incorporationDate: '',
  legalType: null,
  name: '',
  status: null,
  stateFiling: '',
  _error: null,
  _loading: false,
  _stateFilingInfo: null,
} as EntityI)

export const useEntity = () => {
  // functions, etc. to manage the entity state
  const clearEntity = () => {
    entity.amalgamatedInto = null
    entity.bn = ''
    entity.identifier = ''
    entity.incorporationDate = ''
    entity.legalType = null
    entity.name = ''
    entity.status = null
    entity.stateFiling = ''
    entity._error = null
    entity._loading = false
    entity._stateFilingInfo = null
    entity.goodStanding = true
    entity.inDissolution = false
  }
  const loadEntity = async (identifier: string) => {
    entity._loading = true
    const entityInfo = await getEntityInfo(identifier)
    if (entityInfo) {
      setEntity(entityInfo)
      await loadStateFilingInfo()
    }
    entity._loading = false
  }
  /** Loads the public state filing info (used for the historical reason). */
  const loadStateFilingInfo = async () => {
    if (entity.status === BusinessStatuses.HISTORICAL && entity.stateFiling && !entity.amalgamatedInto) {
      entity._stateFilingInfo = await getStateFilingInfo(entity.stateFiling)
    } else {
      entity._stateFilingInfo = null
    }
  }
  const getEntityCode = (description: string): CorpTypeCd => {
    const item = CorpInfoArray.find(obj => (description === obj.fullDesc))
    return (item && item.corpTypeCd) || null
  }
  const getEntityDescription = (entityType: CorpTypeCd) => {
    const item = CorpInfoArray.find(obj => (entityType === obj.corpTypeCd))
    return (item && item.fullDesc) || ''
  }
  const getEntityName = (entity: EntityI) => {
    // return entity.name
    if (!['GP', 'SP'].includes(entity.legalType)) {
      return entity.name
    }
    const primaryName = entity.alternateNames?.find(val => val.identifier === entity.identifier)
    return primaryName?.name || entity.name
  }
  const getEntityInfo = async (identifier: string) => {
    // call legal api for entity data
    const entityInfo = await getEntity(identifier)
    if (entityInfo.error) {
      entity._error = entityInfo.error
      return null
    }
    const resp_entity: EntityI = {
      alternateNames: entityInfo.business.alternateNames,
      amalgamatedInto: entityInfo.business.amalgamatedInto || null,
      bn: entityInfo.business.taxId || '',
      identifier: entityInfo.business.identifier,
      incorporationDate: entityInfo.business.foundingDate,
      legalType: entityInfo.business.legalType,
      name: entityInfo.business.legalName,
      status: entityInfo.business.state,
      stateFiling: entityInfo.business.stateFiling || '',
      goodStanding: entityInfo.business.goodStanding,
      inDissolution: entityInfo.business.inDissolution
    }
    return resp_entity
  }
  const setEntity = (newEntity: EntityI) => {
    entity.amalgamatedInto = newEntity.amalgamatedInto || null
    entity.bn = newEntity.bn || ''
    entity.identifier = newEntity.identifier
    entity.incorporationDate = newEntity.incorporationDate || ''
    entity.legalType = newEntity.legalType
    entity.name = getEntityName(newEntity)
    entity.status = newEntity.status
    entity.stateFiling = newEntity.stateFiling || ''
    entity._stateFilingInfo = newEntity._stateFilingInfo || null
    entity.goodStanding = newEntity.goodStanding
    entity.inDissolution = newEntity.inDissolution
  }

  const isActive = computed(() => {
    return entity.status == BusinessStatuses.ACTIVE
  })

  const isBComp = computed(() => {
    return entity.legalType == CorpTypeCd.BENEFIT_COMPANY
  })

  const isCoop = computed(() => {
    return entity.legalType == CorpTypeCd.COOP
  })

  const isBC = computed(() => {
    return entity.legalType == CorpTypeCd.BC_COMPANY
  })

  const isFirm = computed(() => {
    return entity.legalType == CorpTypeCd.SOLE_PROP || 
    entity.legalType == CorpTypeCd.PARTNERSHIP
  })

  const entityTitle = computed((): string => {
    return isCoop.value ? 'Cooperative Association' : 'Company'
  })

  const actTitle = computed((): string => {
    if (isFirm.value) {
      return 'Partnership Act'
    }
    return isCoop.value ? 'Cooperative Association Act' : 'Business Corporations Act'
  })

  const entityNumberLabel = computed(() => {
    // more rules tbd
    return isCoop.value || isBComp.value ? 'Incorporation Number' : 'Registration Number'
  })

  const corpTypes = computed(() => {
    const nrTypeCodes = [CorpTypeCd.BC_CORPORATION, CorpTypeCd.NR_SOLE_PROP]
    const corpSet = new Set(CorpInfoArray.map((corp) => !nrTypeCodes.includes(corp.corpTypeCd) ? corp.fullDesc : null))
    corpSet.delete(null)
    return [...corpSet]
  })

  const learBusinessTypes = computed(() => {
    return Object.keys(BusinessTypes).map((key) => {
      if (BusinessTypes[key] !== BusinessTypes.BC_LIMITED_COMPANY) return BusinessTypes[key]
    })
  })

  /** The reason this entity is historical (mirrors the business dashboard status badge). */
  const historicalReason = computed((): string => {
    if (entity.status !== BusinessStatuses.HISTORICAL) return ''
    const enDash = '–' // ALT + 0150
    // reason for amalgamation
    if (entity.amalgamatedInto) {
      const amalgamationDate = apiToDate(entity.amalgamatedInto.amalgamationDate)
      const date = dateToPacificDate(amalgamationDate, true)
      const identifier = entity.amalgamatedInto.identifier || 'Unknown Company'
      return `${FilingNames.AMALGAMATION} ${enDash} ${date} ${enDash} ${identifier}`
    }

    const stateFilingInfo = entity._stateFilingInfo
    const filingType = stateFilingInfo?.header?.name
    if (!filingType) return ''

    // reason for dissolution
    if (filingType === FilingTypes.DISSOLUTION) {
      let reason = 'Unknown'
      switch (stateFilingInfo.dissolution?.type) {
        case FilingSubTypes.DISSOLUTION_ADMINISTRATIVE:
          reason = FilingNames.ADMINISTRATIVE_DISSOLUTION
          break
        case FilingSubTypes.DISSOLUTION_INVOLUNTARY:
          reason = FilingNames.INVOLUNTARY_DISSOLUTION
          break
        case FilingSubTypes.DISSOLUTION_VOLUNTARY:
          reason = isFirm.value ? FilingNames.DISSOLUTION : FilingNames.VOLUNTARY_DISSOLUTION
      }
      const date = dateToPacificDate(apiToDate(stateFilingInfo.header.effectiveDate), true)
      return `${reason} ${enDash} ${date}`
    }

    // reason for put back off
    if (filingType === FilingTypes.PUT_BACK_OFF && stateFilingInfo.putBackOff) {
      const date = dateToPacificDate(yyyyMmDdToDate(stateFilingInfo.putBackOff.expiryDate), true)
      return `${stateFilingInfo.putBackOff.reason} on ${date}`
    }

    // reason for continuation out and default reason
    const reason = filingTypeToName(filingType as FilingTypes)
    const date = dateToPacificDateTime(apiToDate(stateFilingInfo.header.effectiveDate))
    return `${reason} ${enDash} ${date}`
  })

  const warnings = computed(() => {
    const warnings = []
    if (entity.inDissolution) {
      warnings.push('INVOLUNTARY_DISSOLUTION')
    }
    if (!entity.goodStanding) {
      warnings.push('NOT_IN_GOOD_STANDING')
    }
    return warnings
  })

  return {
    entity,
    clearEntity,
    getEntityCode,
    getEntityDescription,
    getEntityInfo,
    historicalReason,
    loadEntity,
    loadStateFilingInfo,
    setEntity,
    isActive,
    isBComp,
    isCoop,
    isFirm,
    isBC,
    entityTitle,
    actTitle,
    entityNumberLabel,
    corpTypes,
    learBusinessTypes,
    warnings
  }
}