export const OtherCorpTypes = [
  BusinessTypeE.CO_1860,
  BusinessTypeE.CO_1862,
  BusinessTypeE.CO_1878,
  BusinessTypeE.CO_1890,
  BusinessTypeE.CO_1897,
  BusinessTypeE.CEMETARY,
  BusinessTypeE.EXTRA_PRO_REG,
  BusinessTypeE.FINANCIAL,
  BusinessTypeE.FOREIGN,
  BusinessTypeE.LICENSED,
  BusinessTypeE.MISC_FIRM,
  BusinessTypeE.PARISHES,
  BusinessTypeE.PENSION_FUND_SOCIETY,
  BusinessTypeE.PRIVATE_ACT,
  BusinessTypeE.LIBRARY,
  BusinessTypeE.RAILWAYS,
  BusinessTypeE.REGISTRATION,
  BusinessTypeE.TRAMWAYS,
  BusinessTypeE.TRUST,
  BusinessTypeE.ULC_CO_1860,
  BusinessTypeE.ULC_CO_1862,
  BusinessTypeE.ULC_CO_1878,
  BusinessTypeE.ULC_CO_1890,
  BusinessTypeE.ULC_CO_1897
]

export const ModernizedTypes = [
  BusinessTypeE.BENEFIT_COMPANY,
  BusinessTypeE.COOP,
  BusinessTypeE.PARTNERSHIP,
  BusinessTypeE.SOLE_PROP
]
export const BCLimitedTypes = [BusinessTypeE.CONTINUE_IN, BusinessTypeE.BC_COMPANY]
export const ULCTypes = [BusinessTypeE.ULC_CONTINUE_IN, BusinessTypeE.BC_ULC_COMPANY]
export const SocietyTypes = [BusinessTypeE.CONT_IN_SOCIETY, BusinessTypeE.SOCIETY, BusinessTypeE.SOCIETY_BRANCH]

const corpSet = new Set(CorpInfoArray.map(corp => !OtherCorpTypes.includes(corp.corpTypeCd) ? corp.fullDesc : null))
corpSet.delete(null)
const corpList = [...corpSet].sort()
corpList.push('Other')
export const SearchCorpTypes = corpList
