import { CorpTypeCd, EffectOfOrderTypes, FilingStatus, FilingTypes } from '@/enums'
import { ErrorI } from '@/interfaces'

/**
 * A list item from the API "filings" call (ie, API object).
 * See also History Item interface.
 */
export interface ApiFiling {
  availableOnPaperOnly: boolean
  businessIdentifier: string
  commentsCount: number
  commentsLink: string // URL to fetch this filing's comments
  displayName: string
  documentsLink: string // URL to fetch this filing's documents
  effectiveDate: string // formatted date-time in UTC format
  filingId: number
  filingLink: string // URL to fetch this filing
  isFutureEffective: boolean
  name: FilingTypes
  status: FilingStatus
  submittedDate: string // formatted date-time in UTC format
  submitter: string

  // correction filings only
  correctedFilingId?: string // ID of filing this filing corrects
  correctedLink?: string // URL to fetch filing this filing corrects

  // corrected filings only
  correctionFilingId?: string // ID of this filing's correction
  correctionLink?: string // URL to fetch this filing's correction

  // filing-specific data
  data: {
    applicationDate: string
    legalFilings: Array<string>

    // alteration filings only
    alteration?: {
      fromLegalType?: CorpTypeCd
      toLegalType?: CorpTypeCd
    }

    // AR filings only
    annualReport?: {
      annualGeneralMeetingDate: string
      annualReportDate: string
    }

    // COA filings only
    changeOfAddress?: any // some object

    // COD filings only
    changeOfDirectors?: any // some object

    // conversion filings only
    conversion?: any // some object

    // staff filings only
    order?: {
      effectOfOrder: EffectOfOrderTypes
      fileNumber: string
      orderDate?: string
      orderDetails: string
    }

    // dissolution filings only
    dissolution?: any // some object

    // IA filings only
    incorporationApplication?: any // some object

    // registrar's notation filings only
    registrarsNotation?: any // some object

    // registrar's order filings only
    registrarsOrder?: any // some object

    // special resolution filings only
    specialResolution?: any // some object

    // transition filings only
    transition?: any // some object
  }  
}

export interface ApiDocuments  {
  // contains any number of arbitrarily-named submission level outputs
  // or an array named "legalFilings"
  // eg, certificate, noticeOfArticles, receipt, etc
  [name: string]: string | LegalFiling[] // link to fetch it, or array
}

/** A legal filing object from the API. */
export interface LegalFiling {
  // contains one arbitrarily-named legal filing output
  // whose name is the filing type
  // eg, alteration, annualReport, etc
  [name: string]: string // link to fetch it
}

export interface ApiFilingsRespI {
  error?: ErrorI
  filings?: ApiFiling[]
}
