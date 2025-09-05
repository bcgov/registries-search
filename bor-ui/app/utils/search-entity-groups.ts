export const OtherCorpTypes = [
  BusinessType.CO_1860,
  BusinessType.CO_1862,
  BusinessType.CO_1878,
  BusinessType.CO_1890,
  BusinessType.CO_1897,
  BusinessType.CEMETARY,
  BusinessType.EXTRA_PRO_REG,
  BusinessType.FINANCIAL,
  BusinessType.FOREIGN,
  BusinessType.LICENSED,
  BusinessType.MISC_FIRM,
  BusinessType.PARISHES,
  BusinessType.PENSION_FUND_SOCIETY,
  BusinessType.PRIVATE_ACT,
  BusinessType.LIBRARY,
  BusinessType.RAILWAYS,
  BusinessType.REGISTRATION,
  BusinessType.TRAMWAYS,
  BusinessType.TRUST,
  BusinessType.ULC_CO_1860,
  BusinessType.ULC_CO_1862,
  BusinessType.ULC_CO_1878,
  BusinessType.ULC_CO_1890,
  BusinessType.ULC_CO_1897
]

export const ModernizedTypes = [
  BusinessType.BENEFIT_COMPANY,
  BusinessType.COOP,
  BusinessType.PARTNERSHIP,
  BusinessType.SOLE_PROP
]
export const BCLimitedTypes = [BusinessType.CONTINUE_IN, BusinessType.BC_COMPANY]
export const ULCTypes = [BusinessType.ULC_CONTINUE_IN, BusinessType.BC_ULC_COMPANY]
export const SocietyTypes = [BusinessType.CONT_IN_SOCIETY, BusinessType.SOCIETY, BusinessType.SOCIETY_BRANCH]

const corpSet = new Set(CorpInfoArray.map(corp => !OtherCorpTypes.includes(corp.corpTypeCd) ? corp.fullDesc : null))
corpSet.delete(null)
const corpList = [...corpSet].sort()
corpList.push('Other')
export const SearchCorpTypes = corpList
