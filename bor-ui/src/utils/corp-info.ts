import { BusinessTypeE, CorpClassE } from '#imports'

type CorpInfo = {
  corpTypeCd: BusinessTypeE
  colinInd: boolean
  corpClass: CorpClassE
  shortDesc: string
  fullDesc: string
  numberedDesc?: string
}

/** Array of corp info objects. */
export const CorpInfoArray: Array<CorpInfo> = [
  {
    corpTypeCd: BusinessTypeE.EXTRA_PRO_A,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'EXTRA PRO',
    fullDesc: 'Extraprovincial Company'
  },
  {
    corpTypeCd: BusinessTypeE.EXTRA_PRO_B,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'EXTRA PRO',
    fullDesc: 'Extraprovincial Company'
  },
  {
    corpTypeCd: BusinessTypeE.BENEFIT_COMPANY,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BENEFIT COMPANY',
    fullDesc: 'BC Benefit Company',
    numberedDesc: 'Numbered Benefit Company'
  },
  {
    corpTypeCd: BusinessTypeE.BC_COMPANY,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC COMPANY',
    fullDesc: 'BC Limited Company',
    numberedDesc: 'Numbered Limited Company'
  },
  {
    corpTypeCd: BusinessTypeE.CONTINUE_IN,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CONTINUE IN',
    fullDesc: 'BC Limited Company'
  },
  {
    corpTypeCd: BusinessTypeE.BC_CCC,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC CCC',
    fullDesc: 'BC Community Contribution Company'
  },
  {
    corpTypeCd: BusinessTypeE.CEMETARY,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'CEMETARY',
    fullDesc: 'Cemetary'
  },
  {
    corpTypeCd: BusinessTypeE.COOP,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'COOP',
    fullDesc: 'BC Cooperative Association',
    numberedDesc: 'Numbered Cooperative Association'
  },
  {
    corpTypeCd: BusinessTypeE.BC_ULC_COMPANY,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC ULC COMPANY',
    fullDesc: 'BC Unlimited Liability Company',
    numberedDesc: 'Numbered Unlimited Liability Company'
  },
  {
    corpTypeCd: BusinessTypeE.ULC_CONTINUE_IN,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CONTINUE IN',
    fullDesc: 'BC Unlimited Liability Company'
  },
  {
    corpTypeCd: BusinessTypeE.EXTRA_PRO_REG,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'EXTRA PRO REG',
    fullDesc: 'Extraprovincial Registration'
  },
  {
    corpTypeCd: BusinessTypeE.FINANCIAL,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'FINANCIAL',
    fullDesc: 'Financial Institution'
  },
  {
    corpTypeCd: BusinessTypeE.FOREIGN,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'FOREIGN',
    fullDesc: 'Foreign Registration'
  },
  {
    corpTypeCd: BusinessTypeE.PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'PARTNERSHPI',
    fullDesc: 'BC General Partnership'
  },
  {
    corpTypeCd: BusinessTypeE.LIBRARY,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'LIBRARY',
    fullDesc: 'Public Library Association'
  },
  {
    corpTypeCd: BusinessTypeE.LICENSED,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'LICENSED',
    fullDesc: 'Licensed (Extra-Pro)'
  },
  {
    corpTypeCd: BusinessTypeE.LL_PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'LL PARTNERSHIP',
    fullDesc: 'Limited Liability Partnership'
  },
  {
    corpTypeCd: BusinessTypeE.LIMITED_CO,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'LIMITED CO',
    fullDesc: 'Limited Liability Company'
  },
  {
    corpTypeCd: BusinessTypeE.LIM_PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'LIM PARTNERSHIP',
    fullDesc: 'Limited Partnership'
  },
  {
    corpTypeCd: BusinessTypeE.MISC_FIRM,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'MISC FIRM',
    fullDesc: 'Miscellaneous Firm'
  },
  {
    corpTypeCd: BusinessTypeE.PRIVATE_ACT,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'PRIVATE ACT',
    fullDesc: 'Private Act'
  },
  {
    corpTypeCd: BusinessTypeE.PARISHES,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'PARISHES',
    fullDesc: 'Parishes'
  },
  {
    corpTypeCd: BusinessTypeE.PENSION_FUND_SOCIETY,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'PENS FUND SOCIETY',
    fullDesc: 'Pension Funded Society'
  },
  {
    corpTypeCd: BusinessTypeE.CO_1860,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1860',
    fullDesc: 'CO 1860'
  },
  {
    corpTypeCd: BusinessTypeE.CO_1862,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1862',
    fullDesc: 'CO 1862'
  },
  {
    corpTypeCd: BusinessTypeE.CO_1878,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1878',
    fullDesc: 'CO 1878'
  },
  {
    corpTypeCd: BusinessTypeE.CO_1890,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1890',
    fullDesc: 'CO 1890'
  },
  {
    corpTypeCd: BusinessTypeE.CO_1897,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1897',
    fullDesc: 'CO 1897'
  },
  {
    corpTypeCd: BusinessTypeE.REGISTRATION,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'REGISTRATION',
    fullDesc: 'Registration (Extra-pro)'
  },
  {
    corpTypeCd: BusinessTypeE.RAILWAYS,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'RAILWAYS',
    fullDesc: 'Railways'
  },
  {
    corpTypeCd: BusinessTypeE.SOCIETY,
    colinInd: true,
    corpClass: CorpClassE.SOC,
    shortDesc: 'SOCIETY',
    fullDesc: 'BC Society'
  },
  {
    corpTypeCd: BusinessTypeE.SOCIETY_BRANCH,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'SOCIETY BRANCH',
    fullDesc: 'BC Society'
  },
  {
    corpTypeCd: BusinessTypeE.CONT_IN_SOCIETY,
    colinInd: true,
    corpClass: CorpClassE.SOC,
    shortDesc: 'CONT IN SOCIETY',
    fullDesc: 'BC Society'
  },
  {
    corpTypeCd: BusinessTypeE.SOLE_PROP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'SOLE PROP',
    fullDesc: 'BC Sole Proprietorship'
  },
  {
    corpTypeCd: BusinessTypeE.TRUST,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'TRUST',
    fullDesc: 'Trust'
  },
  {
    corpTypeCd: BusinessTypeE.TRAMWAYS,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'TRAMWAYS',
    fullDesc: 'Tramways'
  },
  {
    corpTypeCd: BusinessTypeE.ULC_CO_1860,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1860',
    fullDesc: 'ULC CO 1860'
  },
  {
    corpTypeCd: BusinessTypeE.ULC_CO_1862,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1862',
    fullDesc: 'ULC CO 1862'
  },
  {
    corpTypeCd: BusinessTypeE.ULC_CO_1878,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1878',
    fullDesc: 'ULC CO 1878'
  },
  {
    corpTypeCd: BusinessTypeE.ULC_CO_1890,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1890',
    fullDesc: 'ULC CO 1890'
  },
  {
    corpTypeCd: BusinessTypeE.ULC_CO_1897,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1897',
    fullDesc: 'ULC CO 1897'
  },
  {
    corpTypeCd: BusinessTypeE.XPRO_COOP,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'XPRO COOP',
    fullDesc: 'Extraprovincial Cooperative Association'
  },
  {
    corpTypeCd: BusinessTypeE.XPRO_LL_PARTNR,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'XPRO LL PARTNR',
    fullDesc: 'Extrapro Limited Liaility Partnership'
  },
  {
    corpTypeCd: BusinessTypeE.XPRO_LIM_PARTNR,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'XPRO LIM PARTNR',
    fullDesc: 'Extraprovincial Limited Partnership'
  },
  {
    corpTypeCd: BusinessTypeE.XPRO_SOCIETY,
    colinInd: true,
    corpClass: CorpClassE.SOC,
    shortDesc: 'XPRO SOCIETY',
    fullDesc: 'Extraprovincial Society'
  }
]

export const getCorpCode = (description: string): BusinessTypeE => {
  const item = CorpInfoArray.find(obj => (description === obj.fullDesc))
  return (item && item.corpTypeCd) || null
}

export const getCorpDescription = (entityType: BusinessTypeE) => {
  const item = CorpInfoArray.find(obj => (entityType === obj.corpTypeCd))
  return (item && item.fullDesc) || ''
}
