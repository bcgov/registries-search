import { CorpTypeCd, FilingTypes } from '@/enums'
import { Document } from '@/types'
import { CommentIF } from '@/interfaces'

/**
 * A Filing History List item (ie, local object).
 * See also Api Filing interface.
 */
export type FilingHistoryItem = {
  availableOnPaperOnly: boolean
  commentsCount: number
  displayName: string
  effectiveDate: Date
  filingId: number
  isFutureEffective: boolean
  name: FilingTypes
  status: string
  submittedDate: Date
  submitter: string

  commentsLink: string // URL to fetch this filing's comments
  documentsLink: string // URL to fetch this filing's documents
  filingLink: string // URL to fetch this filing

  comments: Array<CommentIF>
  documents: Array<Document>

  // correction filings only
  correctedFilingId?: string // ID of filing this filing corrects
  correctedLink?: string // URL to fetch filing this filing corrects

  // corrected filings only
  correctionFilingId?: string // ID of this filing's correction
  correctionLink?: string // URL to fetch this filing's correction

  // IAs only
  isCompletedIa?: boolean
  isFutureEffectiveIa?: boolean
  isFutureEffectiveIaPending?: boolean

  // BCOMP COAs only
  isFutureEffectiveBcompCoaPending?: boolean

  // alterations only
  courtOrderNumber?: string
  isArrangement?: boolean
  isCompletedAlteration?: boolean
  isFutureEffectiveAlteration?: boolean
  isFutureEffectiveAlterationPending?: boolean
  toLegalType?: CorpTypeCd
  fromLegalType?: CorpTypeCd

  // dissolutions only
  isCompletedDissolution?: boolean
  isFutureEffectiveDissolution?: boolean
  isFutureEffectiveDissolutionPending?: boolean

  // staff filings only
  fileNumber?: string
  isTypeStaff?: boolean
  notationOrOrder?: string
  planOfArrangement?: string
}
