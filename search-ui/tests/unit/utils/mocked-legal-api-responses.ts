import { BusinessStatuses, BusinessTypes } from '@/enums'
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