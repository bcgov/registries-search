import { BusinessStatuses, BusinessTypes, FilingStatus, FilingTypes } from '@/enums'
import { LegalApiBusinessI } from '@/interfaces/legal-api-responses'


export const mockedBusinessResp: LegalApiBusinessI = {
  adminFreeze: false,
  arMaxDate: '',
  arMinDate: '',
  complianceWarnings: [],
  fiscalYearEndDate: '',
  foundingDate: '2020-09-30T20:04:42.457859+00:00',
  goodStanding: true,
  hasRestrictions: false,
  identifier: 'CP1234567',
  lastAddressChangeDate: '',
  lastAnnualGeneralMeetingDate: '',
  lastAnnualReportDate: '',
  lastDirectorChangeDate: '',
  lastLedgerTimestamp: '',
  lastModified: '',
  legalName: 'test name',
  legalType: BusinessTypes.COOPERATIVE_ASSOCIATION,
  nextAnnualReport: '',
  state: BusinessStatuses.ACTIVE,
  submitter: '',
  taxId: 'BN00024211133311'
}

export const mockedFilingResp = [
  {
    availableOnPaperOnly: false,
    businessIdentifier: 'BC1218853',
    commentsCount: 0,
    commentsLink: 'https://host/api/v2/businesses/identifier/filings/filingId/comments',
    data: {
      alteration: {},
      applicationDate: '2021-03-11T19:52:43.019672+00:00',
      legalFilings: [
        'alteration'
      ]
    },
    displayName: 'Alteration',
    documentsLink: 'https://host/api/v2/businesses/identifier/filings/filingId/documents',
    effectiveDate: 'Thu, 11 Mar 2021 19:52:43 GMT',
    filingId: 111695,
    filingLink: 'https://host/api/v2/businesses/identifier/filings/filingId',
    isFutureEffective: false,
    name: FilingTypes.ALTERATION,
    status: FilingStatus.COMPLETED,
    submittedDate: 'Thu, 11 Mar 2021 19:52:43 GMT',
    submitter: 'test'
  }
]
