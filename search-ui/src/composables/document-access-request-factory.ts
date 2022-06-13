import { reactive } from 'vue'

import { AccessRequestsHistoryI, DocumentAccessRequestsI, CreateDocumentResponseI } from '@/interfaces'
import { getActiveAccessRequests, createDocumentAccessRequest } from '@/requests'


const documentAccessRequest = reactive({
    requests: [],
    _error: null,
    _loading: false
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
        documentAccessRequest._loading = true

        const createAccessRequestsResponse: CreateDocumentResponseI = await createDocumentAccessRequest(identifier, selectedDocs)
        if (createAccessRequestsResponse.error) {
            documentAccessRequest._error = createAccessRequestsResponse.error
        }        
        documentAccessRequest._loading = false
    }

    return {
        documentAccessRequest,
        clearAccessRequestHistory,
        createAccessRequest,
        loadAccessRequestHistory
    }
}
