import { StaffPaymentOptions } from '@/enums'

export interface BreadcrumbIF {
  text: string
  to?: any
  href?: string
}

/** A comment from the API. */
export interface CommentIF {
  businessId?: string
  comment: string
  filingId?: string
  submitterDisplayName: string
  timestamp: string
}

export interface FormIF extends HTMLFormElement {
  reset(): void;
  resetValidation(): void;
  validate(): boolean;
}

/** A filing's business object from the API. */
export interface StaffPaymentIF {
  option: StaffPaymentOptions
  routingSlipNumber: string
  bcolAccountNumber: string
  datNumber: string
  folioNumber: string
  isPriority: boolean
}


