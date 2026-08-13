import { BusinessStatuses, BusinessTypes } from '@/enums'
import { ErrorI } from '@/interfaces/error'

export interface AmalgamatedIntoI {
  amalgamationDate: string  // i.e. "2024-01-01T08:00:00+00:00"
  amalgamationType: string
  courtApproval: boolean
  identifier: string
  legalName: string
}

/** Slim filing info from the public filing endpoint (filings/{id}?public=true). */
export interface StateFilingI {
  header: {
    name: string,
    effectiveDate?: string  // i.e. "2024-01-01T08:00:00+00:00"
  }
  // filing-specific section keyed by the filing name (i.e. dissolution, putBackOff)
  // holding type, reason, expiryDate, etc. when applicable
  [name: string]: any
}

export interface LegalApiBusinessI {
  adminFreeze: boolean
  alternateNames?: { name: string, identifier: string }[]
  amalgamatedInto?: AmalgamatedIntoI
  arMaxDate: string  // i.e. "2021-11-29"
  arMinDate: string  // i.e. "2021-01-01"
  complianceWarnings: Array<any>
  fiscalYearEndDate: string  // i.e. "2020-09-30"
  foundingDate: string  // i.e. "2020-09-30T20:04:42.457859+00:00"
  goodStanding: boolean
  hasRestrictions: boolean
  identifier: string
  inDissolution: boolean
  lastAddressChangeDate: string  // i.e. "2020-09-30"
  lastAnnualGeneralMeetingDate: string  // i.e. "2020-09-30"
  lastAnnualReportDate: string  // i.e. "2020-09-30"
  lastDirectorChangeDate: string  // i.e. "2020-09-30"
  lastLedgerTimestamp: string  // i.e. "2020-09-30T20:04:42.457859+00:00"
  lastModified: string  // i.e. "2020-09-30T20:04:42.457859+00:00"
  legalName: string
  legalType: BusinessTypes
  // FUTURE: figure out below types when needed
  // naicsCode: null
  // naicsDescription: null
  // naicsKey: null
  nextAnnualReport: string  // i.e. "2020-09-30T20:04:42.457859+00:00"
  state: BusinessStatuses
  stateFiling?: string  // url of the filing that put the business in its current state
  submitter: string  // i.e. "bcsc/xxxxxxxxxxxxxxxxxxxx"
  taxId?: string
}

export interface EntityRespI {
  business?: LegalApiBusinessI
  error?: ErrorI
}