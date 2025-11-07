export interface Doc {
  documentKey: string
  documentType: DocAccessType
  fileName: string
  id: number
}

export interface DocAccess {
  businessIdentifier: string
  businessName?: string
  id: number
  outputFileKey?: string
  paymentCompletionDate?: ApiDateTimeUtc
  paymentToken?: string
  status: string
  submissionDate: ApiDateTimeUtc
  expiryDate: ApiDateTimeUtc
  submitter: string
  documents: Doc[]
  error?: SearchError
}

export interface DocAccessHistory {
  documentAccessRequests?: DocAccess[]
  error?: SearchError
}

export interface DocAccessSubmission {
  business: {
    businessName: string
  }
  documentAccessRequest: {
    documents: { type: DocAccessType }[]
  }
  header?: StaffPayment
}
