import { ErrorI } from '@/interfaces' 

export interface DocumentDetailsI {
    businessIdentifier: string,
    businessName?: string,
    id: number,
    outputFileKey?: string,
    status: string,
    submissionDate: string,
    expiryDate: string,
    submitter: string,
    documents: DocumentI[]
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

export interface AccessRequestsHistoryI {     
    documentAccessRequests?: DocumentDetailsI[],
    error?: ErrorI
}

export interface DocumentAccessRequestsI {     
    requests: DocumentDetailsI[],
    currentRequest: DocumentDetailsI,
    _error: ErrorI,
    _loading: boolean,
    _saving: boolean,
    _downloading: boolean
}

