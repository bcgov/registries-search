import type { DocAccessTypeE, ErrorI } from '#imports'

export interface DocI {
  documentKey: string,
  documentType: DocAccessTypeE,
  fileName: string,
  id: number
}

export interface DocAccessI {
  businessIdentifier: string,
  businessName?: string,
  id: number,
  outputFileKey?: string,
  status: string,
  submissionDate: string,
  expiryDate: string,
  submitter: string,
  documents: DocI[]
}

export interface DocAccessHistoryI {
  documentAccessRequests?: DocAccessI[],
  error?: ErrorI
}
