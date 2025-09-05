type CorpInfo = {
  corpTypeCd: BusinessType
  colinInd: boolean
  corpClass: CorpClass
  shortDesc: string
  fullDesc: string
  numberedDesc?: string
}

/** Array of corp info objects. */
export const CorpInfoArray: Array<CorpInfo> = [
  {
    corpTypeCd: BusinessType.EXTRA_PRO_A,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'EXTRA PRO',
    fullDesc: 'Extraprovincial Company'
  },
  {
    corpTypeCd: BusinessType.EXTRA_PRO_B,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'EXTRA PRO',
    fullDesc: 'Extraprovincial Company'
  },
  {
    corpTypeCd: BusinessType.BENEFIT_COMPANY,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'BENEFIT COMPANY',
    fullDesc: 'BC Benefit Company',
    numberedDesc: 'Numbered Benefit Company'
  },
  {
    corpTypeCd: BusinessType.BC_COMPANY,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'BC COMPANY',
    fullDesc: 'BC Limited Company',
    numberedDesc: 'Numbered Limited Company'
  },
  {
    corpTypeCd: BusinessType.CONTINUE_IN,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'CONTINUE IN',
    fullDesc: 'BC Limited Company'
  },
  {
    corpTypeCd: BusinessType.BC_CCC,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'BC CCC',
    fullDesc: 'BC Community Contribution Company'
  },
  {
    corpTypeCd: BusinessType.CEMETARY,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'CEMETARY',
    fullDesc: 'Cemetary'
  },
  {
    corpTypeCd: BusinessType.COOP,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'COOP',
    fullDesc: 'BC Cooperative Association',
    numberedDesc: 'Numbered Cooperative Association'
  },
  {
    corpTypeCd: BusinessType.BC_ULC_COMPANY,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'BC ULC COMPANY',
    fullDesc: 'BC Unlimited Liability Company',
    numberedDesc: 'Numbered Unlimited Liability Company'
  },
  {
    corpTypeCd: BusinessType.ULC_CONTINUE_IN,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'ULC CONTINUE IN',
    fullDesc: 'BC Unlimited Liability Company'
  },
  {
    corpTypeCd: BusinessType.EXTRA_PRO_REG,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'EXTRA PRO REG',
    fullDesc: 'Extraprovincial Registration'
  },
  {
    corpTypeCd: BusinessType.FINANCIAL,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'FINANCIAL',
    fullDesc: 'Financial Institution'
  },
  {
    corpTypeCd: BusinessType.FOREIGN,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'FOREIGN',
    fullDesc: 'Foreign Registration'
  },
  {
    corpTypeCd: BusinessType.PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'PARTNERSHPI',
    fullDesc: 'BC General Partnership'
  },
  {
    corpTypeCd: BusinessType.LIBRARY,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'LIBRARY',
    fullDesc: 'Public Library Association'
  },
  {
    corpTypeCd: BusinessType.LICENSED,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'LICENSED',
    fullDesc: 'Licensed (Extra-Pro)'
  },
  {
    corpTypeCd: BusinessType.LL_PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'LL PARTNERSHIP',
    fullDesc: 'Limited Liability Partnership'
  },
  {
    corpTypeCd: BusinessType.LIMITED_CO,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'LIMITED CO',
    fullDesc: 'Limited Liability Company'
  },
  {
    corpTypeCd: BusinessType.LIM_PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'LIM PARTNERSHIP',
    fullDesc: 'Limited Partnership'
  },
  {
    corpTypeCd: BusinessType.MISC_FIRM,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'MISC FIRM',
    fullDesc: 'Miscellaneous Firm'
  },
  {
    corpTypeCd: BusinessType.PRIVATE_ACT,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'PRIVATE ACT',
    fullDesc: 'Private Act'
  },
  {
    corpTypeCd: BusinessType.PARISHES,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'PARISHES',
    fullDesc: 'Parishes'
  },
  {
    corpTypeCd: BusinessType.PENSION_FUND_SOCIETY,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'PENS FUND SOCIETY',
    fullDesc: 'Pension Funded Society'
  },
  {
    corpTypeCd: BusinessType.CO_1860,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'CO 1860',
    fullDesc: 'CO 1860'
  },
  {
    corpTypeCd: BusinessType.CO_1862,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'CO 1862',
    fullDesc: 'CO 1862'
  },
  {
    corpTypeCd: BusinessType.CO_1878,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'CO 1878',
    fullDesc: 'CO 1878'
  },
  {
    corpTypeCd: BusinessType.CO_1890,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'CO 1890',
    fullDesc: 'CO 1890'
  },
  {
    corpTypeCd: BusinessType.CO_1897,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'CO 1897',
    fullDesc: 'CO 1897'
  },
  {
    corpTypeCd: BusinessType.REGISTRATION,
    colinInd: true,
    corpClass: CorpClass.XPRO,
    shortDesc: 'REGISTRATION',
    fullDesc: 'Registration (Extra-pro)'
  },
  {
    corpTypeCd: BusinessType.RAILWAYS,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'RAILWAYS',
    fullDesc: 'Railways'
  },
  {
    corpTypeCd: BusinessType.SOCIETY,
    colinInd: true,
    corpClass: CorpClass.SOC,
    shortDesc: 'SOCIETY',
    fullDesc: 'BC Society'
  },
  {
    corpTypeCd: BusinessType.SOCIETY_BRANCH,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'SOCIETY BRANCH',
    fullDesc: 'BC Society'
  },
  {
    corpTypeCd: BusinessType.CONT_IN_SOCIETY,
    colinInd: true,
    corpClass: CorpClass.SOC,
    shortDesc: 'CONT IN SOCIETY',
    fullDesc: 'BC Society'
  },
  {
    corpTypeCd: BusinessType.SOLE_PROP,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'SOLE PROP',
    fullDesc: 'BC Sole Proprietorship'
  },
  {
    corpTypeCd: BusinessType.TRUST,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'TRUST',
    fullDesc: 'Trust'
  },
  {
    corpTypeCd: BusinessType.TRAMWAYS,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'TRAMWAYS',
    fullDesc: 'Tramways'
  },
  {
    corpTypeCd: BusinessType.ULC_CO_1860,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'ULC CO 1860',
    fullDesc: 'ULC CO 1860'
  },
  {
    corpTypeCd: BusinessType.ULC_CO_1862,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'ULC CO 1862',
    fullDesc: 'ULC CO 1862'
  },
  {
    corpTypeCd: BusinessType.ULC_CO_1878,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'ULC CO 1878',
    fullDesc: 'ULC CO 1878'
  },
  {
    corpTypeCd: BusinessType.ULC_CO_1890,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'ULC CO 1890',
    fullDesc: 'ULC CO 1890'
  },
  {
    corpTypeCd: BusinessType.ULC_CO_1897,
    colinInd: true,
    corpClass: CorpClass.BC,
    shortDesc: 'ULC CO 1897',
    fullDesc: 'ULC CO 1897'
  },
  {
    corpTypeCd: BusinessType.XPRO_COOP,
    colinInd: false,
    corpClass: CorpClass.OT,
    shortDesc: 'XPRO COOP',
    fullDesc: 'Extraprovincial Cooperative Association'
  },
  {
    corpTypeCd: BusinessType.XPRO_LL_PARTNR,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'XPRO LL PARTNR',
    fullDesc: 'Extrapro Limited Liaility Partnership'
  },
  {
    corpTypeCd: BusinessType.XPRO_LIM_PARTNR,
    colinInd: true,
    corpClass: CorpClass.FIRM,
    shortDesc: 'XPRO LIM PARTNR',
    fullDesc: 'Extraprovincial Limited Partnership'
  },
  {
    corpTypeCd: BusinessType.XPRO_SOCIETY,
    colinInd: true,
    corpClass: CorpClass.SOC,
    shortDesc: 'XPRO SOCIETY',
    fullDesc: 'Extraprovincial Society'
  }
]

export const getCorpCode = (description: string) => {
  const item = CorpInfoArray.find(obj => (description === obj.fullDesc))
  return (item && item.corpTypeCd) || undefined
}

export const getCorpDescription = (entityType: BusinessType) => {
  const item = CorpInfoArray.find(obj => (entityType === obj.corpTypeCd))
  return (item && item.fullDesc) || ''
}
