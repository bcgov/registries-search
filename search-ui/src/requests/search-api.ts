import { axios } from '@/utils'
import { StatusCodes } from 'http-status-codes'
// local
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { useAuth } from '@/composables'
import {
  SearchResponseI, SuggestionResponseI, DocumentDetailsI,
  CreateDocumentResponseI, AccessRequestsHistoryI, DocumentI, ApiDocuments
} from '@/interfaces'

import { DocumentType, ErrorCategories, ErrorCodes } from '@/enums'
import { DocumentTypeDescriptions } from '@/resources'
import { Document } from '@/types'

const AUTO_SUGGEST_RESULT_SIZE = 10
const SEARCH_RESULT_SIZE = 1000

const getSearchConfig = (params: object = null) => {
  const { auth } = useAuth()
  const url = sessionStorage.getItem('REGISTRY_SEARCH_API_URL')
  const apiKey = window['searchApiKey']
  if (!url) console.error('Error: REGISTRY_SEARCH_API_URL expected, but not found.')
  if (!apiKey) console.error('Error: REGISTRY_SEARCH_API_KEY expected, but not found.')
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)
  
  return { baseURL: url, headers: { 'Account-Id': auth.currentAccount?.id, 'x-apikey': apiKey }, params: params }
}

export async function getAutoComplete(searchValue: string): Promise<SuggestionResponseI> {
  if (!searchValue) return

  const params = { query: searchValue, highlight: true, rows: AUTO_SUGGEST_RESULT_SIZE }
  const config = getSearchConfig(params)
  return axios.get<SuggestionResponseI>('businesses/search/suggest', config)
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

  const params = { query: searchValue, start: 0, rows: SEARCH_RESULT_SIZE }
  const config = getSearchConfig(params)
  return axios.get<SearchResponseI>('businesses/search/facets', config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return {
        searchResults: null,
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.message,
          category: ErrorCategories.SEARCH,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

export async function searchParties(searchValue: string): Promise<SearchResponseI> {
  if (!searchValue) return

  const params = { query: searchValue, categories: 'partyRoles:partner,proprietor', start: 0, rows: SEARCH_RESULT_SIZE }
  const config = getSearchConfig(params)
  return axios.get<SearchResponseI>('businesses/search/parties', config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return {
        searchResults: null,
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.message,
          category: ErrorCategories.SEARCH,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

export async function createDocumentAccessRequest(
  business_identifier: string,
  business_name: string,
  documentList: DocumentType[],
  headerInfo: StaffPaymentIF
): Promise<CreateDocumentResponseI> {
  const config = getSearchConfig()

  const docs = []
  documentList.forEach((doc) => { docs.push({ 'type': doc }) })

  const createRequest = {  
    header: headerInfo,
    business:{ 
      businessName: business_name, 
    },
    documentAccessRequest: {
      documents: docs
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


export async function getActiveAccessRequests(): Promise<AccessRequestsHistoryI> {
  const config = getSearchConfig()
  return axios.get<AccessRequestsHistoryI>(`purchases`,
    config)
    .then(response => {
      const data: AccessRequestsHistoryI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      console.error(error)
      const documentRequests: AccessRequestsHistoryI = {
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

export async function getDocument(businessIdentifier: string, document: DocumentI): Promise<any> {
  const config = getSearchConfig()
  config.headers['Accept'] = 'application/pdf'
  config['responseType'] = 'blob' as 'json'

  return axios.get(`businesses/${businessIdentifier}/documents/${document.documentKey}`,
    config).then(response => {
      if (!response) throw new Error('Null response')
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const fileType = DocumentTypeDescriptions[document.documentType]
      if (window.navigator && window.navigator['msSaveOrOpenBlob']) {
        window.navigator['msSaveOrOpenBlob'](blob, `${fileType}.pdf`)
      } else {
        // for other browsers, create a link pointing to the ObjectURL containing the blob
        const url = window.URL.createObjectURL(blob)
        const a = window.document.createElement('a')
        window.document.body.appendChild(a)
        a.setAttribute('style', 'display: none')
        a.href = url
        a.download = `${fileType}.pdf`
        a.click()
        window.URL.revokeObjectURL(url)
        a.remove()
      }
    }).catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: 'An error occured while downloading the document.',
          category: ErrorCategories.DOCUMENT_DOWNLOAD,
          type: error?.parsed?.rootCause?.type || ErrorCodes.SERVICE_UNAVAILABLE
        }
      }
    })
}


/**
 * Fetches the list of documents belonging to a particular filing
 * 
 * @param businessIdentifier  - The business identifier
 * @param filingId - filing Id 
 * @returns List of documents applicable for the specified filing
 */
export const fetchDocumentList = async (businessIdentifier: string, filingId: number): Promise<ApiDocuments> => {
  const config = getSearchConfig()
  return axios.get<any>(`businesses/${businessIdentifier}/documents/filings/${filingId}`, config)
    .then(response => {
      const data = response?.data?.documents
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategories.ENTITY_BASIC,
          type: error?.parsed?.rootCause?.type || ErrorCodes.SERVICE_UNAVAILABLE
        }
      }
    })
}

/**
   * Fetches a document and prompts browser to open/save it.
   * @param document the document info object
   */
export const fetchFilingDocument = (businessIdentifier: string, filingId: number, document: Document): Promise<any> => {
  const config = getSearchConfig()
  config.headers['Accept'] = 'application/pdf'
  config['responseType'] = 'blob' as 'json'
  const documentType = document.link.split('/').pop()
  return axios.get(`businesses/${businessIdentifier}/documents/filings/${filingId}/${documentType}`, config)
    .then(response => {
      if (!response) throw new Error('Null response')
      const blob = new Blob([response.data], { type: 'application/pdf' })

      if (window.navigator && window.navigator['msSaveOrOpenBlob']) {
        window.navigator['msSaveOrOpenBlob'](blob, document.filename)
      } else {
        const url = window.URL.createObjectURL(blob)
        const a = window.document.createElement('a')
        window.document.body.appendChild(a)
        a.setAttribute('style', 'display: none')
        a.href = url
        a.download = document.filename
        a.click()
        window.URL.revokeObjectURL(url)
        a.remove()
      }
    }).catch(error => {
      return {
        error: {
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: 'An error occured while downloading the document.',
          category: ErrorCategories.DOCUMENT_DOWNLOAD,
          type: error?.parsed?.rootCause?.type || ErrorCodes.SERVICE_UNAVAILABLE
        }
      }
    })
}
