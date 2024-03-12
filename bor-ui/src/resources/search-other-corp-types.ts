import { CorpTypeCdE } from '@/enums'
import { CorpInfoArray } from '@/resources'

export const NrTypes = [CorpTypeCdE.BC_CORPORATION, CorpTypeCdE.NR_SOLE_PROP]
export const OtherCorpTypes = [
  CorpTypeCdE.CO_1860,
  CorpTypeCdE.CO_1862,
  CorpTypeCdE.CO_1878,
  CorpTypeCdE.CO_1890,
  CorpTypeCdE.CO_1897,
  CorpTypeCdE.CEMETARY,
  CorpTypeCdE.EXTRA_PRO_REG,
  CorpTypeCdE.FINANCIAL,
  CorpTypeCdE.FOREIGN,
  CorpTypeCdE.LICENSED,
  CorpTypeCdE.MISC_FIRM,
  CorpTypeCdE.PARISHES,
  CorpTypeCdE.PENSION_FUND_SOCIETY,
  CorpTypeCdE.PRIVATE_ACT,
  CorpTypeCdE.LIBRARY,
  CorpTypeCdE.RAILWAYS,
  CorpTypeCdE.REGISTRATION,
  CorpTypeCdE.TRAMWAYS,
  CorpTypeCdE.TRUST,
  CorpTypeCdE.ULC_CO_1860,
  CorpTypeCdE.ULC_CO_1862,
  CorpTypeCdE.ULC_CO_1878,
  CorpTypeCdE.ULC_CO_1890,
  CorpTypeCdE.ULC_CO_1897
]
const ignoredTypes = [...NrTypes, ...OtherCorpTypes]

const corpSet = new Set(CorpInfoArray.map(corp => !ignoredTypes.includes(corp.corpTypeCd) ? corp.fullDesc : null))
corpSet.delete(null)
const corpList = [...corpSet].sort()
corpList.push('Other')
export const SearchCorpTypes = corpList
