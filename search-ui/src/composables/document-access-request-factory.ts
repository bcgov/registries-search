import { reactive } from 'vue'

import { DocumentType, ErrorCategories } from '@/enums'
import {
    AccessRequestsHistoryI,
    CreateDocumentResponseI,
    DocumentAccessRequestsI,
    DocumentI,
    StaffPaymentIF
} from '@/interfaces'
import { EntityI } from '@/interfaces/entity'
import {
    cancelDocumentAccessRequestById,
    createDocumentAccessRequest,
    fetchFilingDocument,
    getActiveAccessRequests,
    getDocument,
    getDocumentAccessRequestsById
} from '@/requests'
import { Document } from '@/types'
import { DocumentAccessRequestStatus } from '@/enums/document-access-request'


const documentAccessRequest = reactive({
    requests: [],
    currentRequest: null,
    _error: null,
    _loading: false,
    _saving: false,
    _downloading: false,
    _needsPayment: false
}) as DocumentAccessRequestsI

export const useDocumentAccessRequest = () => {
    // functions  to manage the filing history
    const clearAccessRequestHistory = () => {
        documentAccessRequest._error = null
        documentAccessRequest.requests = []
    }


    const loadAccessRequestHistory = async () => {
        documentAccessRequest._loading = true
        clearAccessRequestHistory()
        const accessRequestsResponse: AccessRequestsHistoryI = await getActiveAccessRequests()
        if (accessRequestsResponse.error) {
            documentAccessRequest._error = accessRequestsResponse.error
        }
        else {
            documentAccessRequest.requests = accessRequestsResponse.documentAccessRequests
        }
        documentAccessRequest._loading = false
    }

    const getAccessRequestById = async (documentAccessRequestId: number) => {
        documentAccessRequest._loading = true
        clearAccessRequestHistory()
        const accessRequestsResponse: AccessRequestsHistoryI
          = await getDocumentAccessRequestsById(documentAccessRequestId)
        if (accessRequestsResponse.error) {
            documentAccessRequest._error = accessRequestsResponse.error
        } else {
            documentAccessRequest.currentRequest = accessRequestsResponse.documentAccessRequest
        }
        documentAccessRequest._loading = false
    }
    const createAccessRequest = async (selectedDocs: DocumentType[], entity: EntityI, header: StaffPaymentIF) => {
        documentAccessRequest._saving = true
        documentAccessRequest._error = null
        const response: CreateDocumentResponseI = await createDocumentAccessRequest(entity.identifier, entity.name,
             selectedDocs, header)
        if (response.error) {
            documentAccessRequest._error = response.error
        } else {
            documentAccessRequest.currentRequest = response.createDocumentResponse
            if(documentAccessRequest.currentRequest.status === DocumentAccessRequestStatus.CREATED) {
                documentAccessRequest._needsPayment = true
            }
        }
        documentAccessRequest._saving = false
    }

    const cancelAccessRequest = async (entity: EntityI, darId: number) => {
        documentAccessRequest._saving = true
        documentAccessRequest._error = null
        const response
          = await cancelDocumentAccessRequestById(entity.identifier, darId)
        if (response.error) {
            documentAccessRequest._error = response.error
        } else {
            documentAccessRequest._needsPayment = false
        }
        documentAccessRequest._saving = false
        // show payment canceled dialog
        documentAccessRequest._error = {
            category: ErrorCategories.DOCUMENT_ACCESS_PAYMENT_CANCELLED,
            detail: 'not used',
            message: 'not used',
            statusCode: null,
            type: null
        }
        return
    }

    const downloadDocument = async (businessIdentifier: string, document: DocumentI) => {
        documentAccessRequest._downloading = true
        documentAccessRequest._error = null
        const response = await getDocument(businessIdentifier, document)
        if (response?.error){
            documentAccessRequest._error = response.error
        }
        documentAccessRequest._downloading = false
    }

    const downloadFilingDocument = async (businessIdentifier: string, filingId: number, document: Document) => {
        documentAccessRequest._downloading = true
        documentAccessRequest._error = null
        const response = await fetchFilingDocument(businessIdentifier, filingId, document)
        if (response?.error){
            documentAccessRequest._error = response.error
        }
        documentAccessRequest._downloading = false
     }

    return {
        documentAccessRequest,
        cancelAccessRequest,
        clearAccessRequestHistory,
        createAccessRequest,
        loadAccessRequestHistory,
        getAccessRequestById,
        downloadDocument,
        downloadFilingDocument
    }
}
