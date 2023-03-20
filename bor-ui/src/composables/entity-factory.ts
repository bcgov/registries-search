import { computed } from 'vue'
// Local
import { BusinessTypes, CorpTypeCd } from '@/enums'
import { CorpInfoArray } from '@/resources'

export const useEntity = () => {
  // entity helpers
  const getEntityCode = (description: string): CorpTypeCd => {
    const item = CorpInfoArray.find(obj => (description === obj.fullDesc))
    return (item && item.corpTypeCd) || null
  }

  const getEntityDescription = (entityType: CorpTypeCd) => {
    const item = CorpInfoArray.find(obj => (entityType === obj.corpTypeCd))
    return (item && item.fullDesc) || ''
  }

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

  return {
    getEntityCode,
    getEntityDescription,
    corpTypes,
    learBusinessTypes,
  }
}