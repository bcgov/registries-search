import { reactive } from 'vue'

import { DocumentType } from '@/enums'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { AccessRequestsHistoryI, DocumentAccessRequestsI, CreateDocumentResponseI, DocumentI } from '@/interfaces'
import { EntityI } from '@/interfaces/entity'
import { getActiveAccessRequests, createDocumentAccessRequest, getDocument, fetchFilingDocument } from '@/requests'
import {  Document } from '@/types'


const documentAccessRequest = reactive({
    requests: [],
    currentRequest: null,
    _error: null,
    _loading: false,
    _saving: false,
    _downloading: false
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

    const createAccessRequest = async (selectedDocs: DocumentType[], entity: EntityI, header: StaffPaymentIF) => {
        documentAccessRequest._saving = true
        documentAccessRequest._error = null
        const response: CreateDocumentResponseI = await createDocumentAccessRequest(entity.identifier, entity.name,
             selectedDocs, header)
        if (response.error) {
            documentAccessRequest._error = response.error
        } else {
            documentAccessRequest.currentRequest = response.createDocumentResponse
        }        
        documentAccessRequest._saving = false
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
        clearAccessRequestHistory,
        createAccessRequest,
        loadAccessRequestHistory,
        downloadDocument,
        downloadFilingDocument
    }
}
