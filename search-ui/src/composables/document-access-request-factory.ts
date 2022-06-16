import { reactive } from 'vue'

import { AccessRequestsHistoryI, DocumentAccessRequestsI, CreateDocumentResponseI, DocumentI } from '@/interfaces'
import { getActiveAccessRequests, createDocumentAccessRequest, getDocument, fetchFilingDocument } from '@/requests'
import {  Document } from '@/types'


const documentAccessRequest = reactive({
    requests: [],
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


    const loadAccessRequestHistory = async (identifier: string) => {
        documentAccessRequest._loading = true
        clearAccessRequestHistory()
        const accessRequestsResponse: AccessRequestsHistoryI = await getActiveAccessRequests(identifier)
        if (accessRequestsResponse.error) {
            documentAccessRequest._error = accessRequestsResponse.error
        }
        else {
            documentAccessRequest.requests = accessRequestsResponse.documentAccessRequests
        }
        documentAccessRequest._loading = false
    }

    const createAccessRequest = async (identifier: string, selectedDocs: any) => {
        documentAccessRequest._saving = true

        const response: CreateDocumentResponseI = await createDocumentAccessRequest(identifier, selectedDocs)
        if (response.error) {
            documentAccessRequest._error = response.error
        }        
        documentAccessRequest._saving = false
    }

    const downloadDocument = async (businessIdentifier: string, document: DocumentI) => {
        documentAccessRequest._downloading = true
        await getDocument(businessIdentifier, document)          
        documentAccessRequest._downloading = false
    }

    const downloadFilingDocument = async (businessIdentifier: string, filingId: number, document: Document) => {     
        documentAccessRequest._downloading = true
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
