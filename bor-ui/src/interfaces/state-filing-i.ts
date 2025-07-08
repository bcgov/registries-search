import { FilingTypes } from '@bcrs-shared-components/enums'

import { FilingStatusE } from '~/enums/filing-status-e'

export interface StateFilingHeaderI {
  accountId?: number // NOT USED
  ARFilingYear?: number // ARs only
  arMaxDate?: string // ARs only
  arMinDate?: string // ARs only
  availableOnPaperOnly?: boolean // non-tasks only
  certifiedBy: string // FUTURE: is this obsolete?
  comments: any[]
  commentsCount: number
  commentsLink: string
  date: string // submitted date
  documentsLink: string
  effectiveDate: string // FUTURE: is this obsolete?
  email?: string // FUTURE: is this obsolete?
  filingId: number
  filingLink: string
  inColinOnly?: boolean // FUTURE: is this obsolete?
  isCorrected: boolean
  isCorrectionPending: boolean
  isFutureEffective: boolean // FUTURE: is this obsolete?
  name: FilingTypes
  paymentMethod?: any
  paymentStatusCode?: string
  paymentToken?: any // NB: may be UUID in future
  priority?: boolean // alterations and corrections only
  status: FilingStatusE
  submitter: string // FUTURE: is this obsolete?
}
