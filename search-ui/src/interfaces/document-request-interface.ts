import { ErrorI } from '@/interfaces'
import {
    DocumentAccessRequestStatus
} from '@/enums/document-access-request'

export interface DocumentDetailsI {
    businessIdentifier: string,
    businessName?: string,
    id: number,
    outputFileKey?: string,
    status: DocumentAccessRequestStatus,
    submissionDate: string,
    expiryDate: string,
    submitter: string,
    documents: DocumentI[]
    paymentStatus: string
    paymentToken: string
    paymentCompletionDate?: string
}

// api responses
export interface CreateDocumentResponseI {
    createDocumentResponse?: DocumentDetailsI,
    error?: ErrorI
}

export interface DocumentI {
    documentKey: string,
    documentType: string,
    fileName: string,
    id: number
}

/**
 * This Interface contains possible responses from the /purchases and /purchases/darId POST endpoint
 *
 * Depending on what endpoint is called it will return following:
 * - if endpoint hit is /purchases, it returns error response or list of DocumentDetailsI
 * - if endpoint hit is /purchases/darId returns either DocumentDetailsI for that specific document access request
 *   or it returns error response
 */
export interface AccessRequestsHistoryI {
    documentAccessRequests?: DocumentDetailsI[],
    documentAccessRequest?: DocumentDetailsI,
    error?: ErrorI
}

export interface DocumentAccessRequestsI {
    requests: DocumentDetailsI[],
    currentRequest: DocumentDetailsI,
    _error: ErrorI,
    _loading: boolean,
    _saving: boolean,
    _downloading: boolean,
    _needsPayment: boolean
}
