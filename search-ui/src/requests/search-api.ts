import { axios } from '@/utils'
import { StatusCodes } from 'http-status-codes'
// local
import { useAuth } from '@/composables'
import { SearchResponseI, SuggestionResponseI, DocumentDetailsI,
   CreateDocumentResponseI,  AccessRequestsHistoryI } from '@/interfaces'
import { ErrorCategories } from '@/enums'

const AUTO_SUGGEST_RESULT_SIZE = 10

export async function getAutoComplete(searchValue: string): Promise<SuggestionResponseI> {
  if (!searchValue) return

  const url = sessionStorage.getItem('REGISTRY_SEARCH_API_URL')
  if (!url) console.error('Error: REGISTRY_SEARCH_API_URL expected, but not found.')
  const config = { baseURL: url }
  return axios.get<SuggestionResponseI>
    (`businesses/search/suggest?query=${searchValue}&max_results=${AUTO_SUGGEST_RESULT_SIZE}`,
      config)
    .then(response => {
      const data: SuggestionResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return {
        results: [],
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.message,
          category: ErrorCategories.SEARCH,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

export async function searchBusiness(searchValue: string): Promise<SearchResponseI> {
  if (!searchValue) return

  const url = sessionStorage.getItem('REGISTRY_SEARCH_API_URL')
  const config = { baseURL: url }
  return axios.get<SearchResponseI>(`businesses/search/facets?query=${searchValue}&start_row=0&num_of_rows=100`,
    config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return {
        results: [],
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.message,
          category: ErrorCategories.SEARCH,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}


export async function createDocumentAccessRequest(business_identifier: string,
   documentList: any): Promise<CreateDocumentResponseI> {
  const url = sessionStorage.getItem('REGISTRY_SEARCH_API_URL')
  const { auth } = useAuth()
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)
  const config = { baseURL: url, headers: { 'accountId': auth.currentAccount.id }}

  const docs = []
  documentList.value.forEach((doc) => { docs.push({ 'type': doc }) })

  const createRequest = {
    "documentAccessRequest": {
      "documents": docs
    }
  }
  return axios.post<DocumentDetailsI>(`businesses/${business_identifier}/documents/requests`, createRequest,
    config)
    .then(response => {
      const data: DocumentDetailsI = response?.data
      const createAccessResponse: CreateDocumentResponseI = {
        createDocumentResponse: data
      }
      return createAccessResponse
    }).catch(error => {
      const createAccessResponse: CreateDocumentResponseI = {
        error:
        {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategories.CREATE_DOCUMENT_ACCESS_REQUEST,
          type: error?.parsed?.rootCause?.type
        }
      }
      return createAccessResponse
    })
}


export async function getActiveAccessRequests(business_identifier: string): Promise<AccessRequestsHistoryI> {
  const url = sessionStorage.getItem('REGISTRY_SEARCH_API_URL')
  const { auth } = useAuth()
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)
  const config = { baseURL: url, headers: { 'accountId': auth.currentAccount.id }}
  return axios.get< AccessRequestsHistoryI>(`businesses/${business_identifier}/documents/requests`,
    config)
    .then(response => {
      const data:  AccessRequestsHistoryI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      console.error(error)
      const documentRequests:  AccessRequestsHistoryI = {
        error:
        {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategories.CREATE_DOCUMENT_ACCESS_REQUEST,
          type: error?.parsed?.rootCause?.type
        }
      }
      return documentRequests
    })
}