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
  status: string
  submissionDate: string
  expiryDate: string
  submitter: string
  documents: Doc[]
}

export interface DocAccessHistory {
  documentAccessRequests?: DocAccess[]
  error?: SearchError
}
