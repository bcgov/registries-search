import { CorpTypeCd } from '@/enums'
import { CorpInfoArray } from '@/resources'

export const NrTypes = [CorpTypeCd.BC_CORPORATION, CorpTypeCd.NR_SOLE_PROP]
export const OtherCorpTypes = [
  CorpTypeCd.CO_1860,
  CorpTypeCd.CO_1862,
  CorpTypeCd.CO_1878,
  CorpTypeCd.CO_1890,
  CorpTypeCd.CO_1897,
  CorpTypeCd.CEMETARY,
  CorpTypeCd.EXTRA_PRO_REG,
  CorpTypeCd.FINANCIAL,
  CorpTypeCd.FOREIGN,
  CorpTypeCd.LICENSED,
  CorpTypeCd.MISC_FIRM,
  CorpTypeCd.PARISHES,
  CorpTypeCd.PENSION_FUND_SOCIETY,
  CorpTypeCd.PRIVATE_ACT,
  CorpTypeCd.LIBRARY,
  CorpTypeCd.RAILWAYS,
  CorpTypeCd.REGISTRATION,
  CorpTypeCd.TRAMWAYS,
  CorpTypeCd.TRUST,
  CorpTypeCd.ULC_CO_1860,
  CorpTypeCd.ULC_CO_1862,
  CorpTypeCd.ULC_CO_1878,
  CorpTypeCd.ULC_CO_1890,
  CorpTypeCd.ULC_CO_1897
]
const ignoredTypes = [...NrTypes, ...OtherCorpTypes]

const corpSet = new Set(CorpInfoArray.map((corp) => !ignoredTypes.includes(corp.corpTypeCd) ? corp.fullDesc : null))
corpSet.delete(null)
const corpList = [...corpSet].sort()
corpList.push('Other')
export const SearchCorpTypes = corpList
