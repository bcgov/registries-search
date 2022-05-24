import { BusinessStatuses, BusinessTypes } from '@/enums'
import { ErrorI } from '@/interfaces/error'

export interface LegalApiBusinessI {
  adminFreeze: boolean
  arMaxDate: string  // i.e. "2021-11-29"
  arMinDate: string  // i.e. "2021-01-01"
  complianceWarnings: Array<any>
  fiscalYearEndDate: string  // i.e. "2020-09-30"
  foundingDate: string  // i.e. "2020-09-30T20:04:42.457859+00:00"
  goodStanding: boolean
  hasRestrictions: boolean
  identifier: string
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
  submitter: string  // i.e. "bcsc/xxxxxxxxxxxxxxxxxxxx"
  taxId?: string
}

export interface EntityRespI {
  business?: LegalApiBusinessI
  error?: ErrorI
}