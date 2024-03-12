import { CorpClassE, CorpTypeCdE } from '@/enums'

export type CorpInfo = {
  corpTypeCd: CorpTypeCdE
  colinInd: boolean
  corpClass: CorpClassE
  shortDesc: string
  fullDesc: string
  numberedDesc?: string
}
