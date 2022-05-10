import { CorpClass, CorpTypeCd } from '@/enums'

export type CorpInfo = {
    corpTypeCd: CorpTypeCd
    colinInd: boolean
    corpClass: CorpClass
    shortDesc: string
    fullDesc: string
    numberedDesc?: string
}