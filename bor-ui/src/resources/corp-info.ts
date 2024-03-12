import { CorpInfo } from '@/types'

/** Array of corp info objects. */
export const CorpInfoArray: Array<CorpInfo> = [
  {
    corpTypeCd: CorpTypeCdE.EXTRA_PRO_A,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'EXTRA PRO',
    fullDesc: 'Extraprovincial Company'
  }, {
    corpTypeCd: CorpTypeCdE.EXTRA_PRO_B,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'EXTRA PRO',
    fullDesc: 'Extraprovincial Company'
  }, {
    corpTypeCd: CorpTypeCdE.BENEFIT_COMPANY,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BENEFIT COMPANY',
    fullDesc: 'BC Benefit Company',
    numberedDesc: 'Numbered Benefit Company'
  }, {
    corpTypeCd: CorpTypeCdE.BC_COMPANY,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC COMPANY',
    fullDesc: 'BC Limited Company',
    numberedDesc: 'Numbered Limited Company'
  }, {
    corpTypeCd: CorpTypeCdE.CONTINUE_IN,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CONTINUE IN',
    fullDesc: 'BC Limited Company'
  }, {
    corpTypeCd: CorpTypeCdE.BC_CCC,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC CCC',
    fullDesc: 'BC Community Contribution Company'
  }, {
    corpTypeCd: CorpTypeCdE.CEMETARY,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'CEMETARY',
    fullDesc: 'Cemetary'
  }, {
    corpTypeCd: CorpTypeCdE.COOP,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'COOP',
    fullDesc: 'BC Cooperative Association',
    numberedDesc: 'Numbered Cooperative Association'
  }, {
    // SPECIAL NAMEREQUEST-ONLY ENTITY TYPE
    corpTypeCd: CorpTypeCdE.BC_CORPORATION,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC COMPANY',
    fullDesc: 'BC Company', // BC Company - Incorporation/Amalgamation
    numberedDesc: 'Numbered Company'
  }, {
    corpTypeCd: CorpTypeCdE.BC_ULC_COMPANY,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'BC ULC COMPANY',
    fullDesc: 'BC Unlimited Liability Company',
    numberedDesc: 'Numbered Unlimited Liability Company'
  }, {
    corpTypeCd: CorpTypeCdE.ULC_CONTINUE_IN,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CONTINUE IN',
    fullDesc: 'BC Unlimited Liability Company'
  }, {
    corpTypeCd: CorpTypeCdE.EXTRA_PRO_REG,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'EXTRA PRO REG',
    fullDesc: 'Extraprovincial Registration'
  }, {
    corpTypeCd: CorpTypeCdE.FINANCIAL,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'FINANCIAL',
    fullDesc: 'Financial Institution'
  }, {
    corpTypeCd: CorpTypeCdE.FOREIGN,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'FOREIGN',
    fullDesc: 'Foreign Registration'
  }, {
    corpTypeCd: CorpTypeCdE.NR_SOLE_PROP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'SOLE PROP',
    fullDesc: 'Sole Proprietorship'
  }, {
    corpTypeCd: CorpTypeCdE.PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'PARTNERSHPI',
    fullDesc: 'BC General Partnership'
  }, {
    corpTypeCd: CorpTypeCdE.LIBRARY,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'LIBRARY',
    fullDesc: 'Public Library Association'
  }, {
    corpTypeCd: CorpTypeCdE.LICENSED,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'LICENSED',
    fullDesc: 'Licensed (Extra-Pro)'
  }, {
    corpTypeCd: CorpTypeCdE.LL_PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'LL PARTNERSHIP',
    fullDesc: 'Limited Liability Partnership'
  }, {
    corpTypeCd: CorpTypeCdE.LIMITED_CO,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'LIMITED CO',
    fullDesc: 'Limited Liability Company'
  }, {
    corpTypeCd: CorpTypeCdE.LIM_PARTNERSHIP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'LIM PARTNERSHIP',
    fullDesc: 'Limited Partnership'
  }, {
    corpTypeCd: CorpTypeCdE.MISC_FIRM,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'MISC FIRM',
    fullDesc: 'Miscellaneous Firm'
  }, {
    corpTypeCd: CorpTypeCdE.PRIVATE_ACT,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'PRIVATE ACT',
    fullDesc: 'Private Act'
  }, {
    corpTypeCd: CorpTypeCdE.PARISHES,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'PARISHES',
    fullDesc: 'Parishes'
  }, {
    corpTypeCd: CorpTypeCdE.PENSION_FUND_SOCIETY,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'PENS FUND SOCIETY',
    fullDesc: 'Pension Funded Society'
  }, {
    corpTypeCd: CorpTypeCdE.CO_1860,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1860',
    fullDesc: 'CO 1860'
  }, {
    corpTypeCd: CorpTypeCdE.CO_1862,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1862',
    fullDesc: 'CO 1862'
  }, {
    corpTypeCd: CorpTypeCdE.CO_1878,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1878',
    fullDesc: 'CO 1878'
  }, {
    corpTypeCd: CorpTypeCdE.CO_1890,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1890',
    fullDesc: 'CO 1890'
  }, {
    corpTypeCd: CorpTypeCdE.CO_1897,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'CO 1897',
    fullDesc: 'CO 1897'
  }, {
    corpTypeCd: CorpTypeCdE.REGISTRATION,
    colinInd: true,
    corpClass: CorpClassE.XPRO,
    shortDesc: 'REGISTRATION',
    fullDesc: 'Registration (Extra-pro)'
  }, {
    corpTypeCd: CorpTypeCdE.RAILWAYS,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'RAILWAYS',
    fullDesc: 'Railways'
  }, {
    corpTypeCd: CorpTypeCdE.SOCIETY,
    colinInd: true,
    corpClass: CorpClassE.SOC,
    shortDesc: 'SOCIETY',
    fullDesc: 'BC Society'
  }, {
    corpTypeCd: CorpTypeCdE.SOCIETY_BRANCH,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'SOCIETY BRANCH',
    fullDesc: 'BC Society'
  }, {
    corpTypeCd: CorpTypeCdE.CONT_IN_SOCIETY,
    colinInd: true,
    corpClass: CorpClassE.SOC,
    shortDesc: 'CONT IN SOCIETY',
    fullDesc: 'BC Society'
  }, {
    corpTypeCd: CorpTypeCdE.SOLE_PROP,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'SOLE PROP',
    fullDesc: 'BC Sole Proprietorship'
  }, {
    corpTypeCd: CorpTypeCdE.TRUST,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'TRUST',
    fullDesc: 'Trust'
  }, {
    corpTypeCd: CorpTypeCdE.TRAMWAYS,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'TRAMWAYS',
    fullDesc: 'Tramways'
  }, {
    corpTypeCd: CorpTypeCdE.ULC_CO_1860,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1860',
    fullDesc: 'ULC CO 1860'
  }, {
    corpTypeCd: CorpTypeCdE.ULC_CO_1862,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1862',
    fullDesc: 'ULC CO 1862'
  }, {
    corpTypeCd: CorpTypeCdE.ULC_CO_1878,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1878',
    fullDesc: 'ULC CO 1878'
  }, {
    corpTypeCd: CorpTypeCdE.ULC_CO_1890,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1890',
    fullDesc: 'ULC CO 1890'
  }, {
    corpTypeCd: CorpTypeCdE.ULC_CO_1897,
    colinInd: true,
    corpClass: CorpClassE.BC,
    shortDesc: 'ULC CO 1897',
    fullDesc: 'ULC CO 1897'
  }, {
    corpTypeCd: CorpTypeCdE.XPRO_COOP,
    colinInd: false,
    corpClass: CorpClassE.OT,
    shortDesc: 'XPRO COOP',
    fullDesc: 'Extraprovincial Cooperative Association'
  }, {
    corpTypeCd: CorpTypeCdE.XPRO_LL_PARTNR,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'XPRO LL PARTNR',
    fullDesc: 'Extrapro Limited Liaility Partnership'
  }, {
    corpTypeCd: CorpTypeCdE.XPRO_LIM_PARTNR,
    colinInd: true,
    corpClass: CorpClassE.FIRM,
    shortDesc: 'XPRO LIM PARTNR',
    fullDesc: 'Extraprovincial Limited Partnership'
  }, {
    corpTypeCd: CorpTypeCdE.XPRO_SOCIETY,
    colinInd: true,
    corpClass: CorpClassE.SOC,
    shortDesc: 'XPRO SOCIETY',
    fullDesc: 'Extraprovincial Society'
  }
]
