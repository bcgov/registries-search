import { axios } from '@/utils'
import { StatusCodes } from 'http-status-codes'
// local
import { StaffPaymentIF } from '@/bcrs-common-components/interfaces'
import { useAuth } from '@/composables'
import {
  SearchResponseI, SuggestionResponseI, DocumentDetailsI,
  CreateDocumentResponseI, AccessRequestsHistoryI, DocumentI, ApiDocuments, SearchFilterI, SearchPartyFilterI
} from '@/interfaces'

import { DocumentType, ErrorCategories, ErrorCodes } from '@/enums'
import { DocumentTypeDescriptions } from '@/resources'
import { Document } from '@/types'
import { StaffPaymentOptions } from '@/bcrs-common-components/enums'

const AUTO_SUGGEST_RESULT_SIZE = 10

const addSearchBusFilters = (filters: SearchFilterI) => {
  const filterParams = { query: '', categories: '' }
  // filters
  if (filters?.bn) filterParams.query += `::bn:${filters.bn}`
  if (filters?.identifier) filterParams.query += `::identifier:${filters.identifier}`
  if (filters?.name) filterParams.query += `::name:${filters.name}`
  // categories
  if (filters?.legalType) filterParams.categories += `legalType:${filters.legalType}`
  if (filters?.status) {
    filterParams.categories += filters?.legalType ? `::` : ''
    filterParams.categories += `status:${filters.status}`
  }
  return filterParams
}

const addSearchPartyFilters = (filters: SearchPartyFilterI) => {
  const filterParams = { query: '', categories: '' }
  // filters
  if (filters.parentBN) filterParams.query += `::parentBN:${filters.parentBN}`
  if (filters.parentIdentifier) filterParams.query += `::parentIdentifier:${filters.parentIdentifier}`
  if (filters.parentName) filterParams.query += `::parentName:${filters.parentName}`
  if (filters.partyName) filterParams.query += `::partyName:${filters.partyName}`
  // categories
  if (filters.partyRoles) filterParams.categories += `partyRoles:${filters.partyRoles}`
  else filterParams.categories += 'partyRoles:partner,proprietor'
  if (filters.parentStatus) filterParams.categories += `::parentStatus:${filters.parentStatus}`

  return filterParams
}

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
      let category = ErrorCategories.SEARCH
      if (error?.response?.status === StatusCodes.SERVICE_UNAVAILABLE) category = ErrorCategories.SEARCH_UNAVAILABLE
      return {
        results: [],
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.message,
          category: category,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

export async function searchBusiness(
  searchValue: string,
  filters: SearchFilterI,
  rows: number,
  start: number
): Promise<SearchResponseI> {
  if (!searchValue) return
  // basic params
  const params = { query: `value:${searchValue}`, start: start * rows, rows: rows }
  // add filters
  const filterParams = addSearchBusFilters(filters)
  if (filterParams.query) params.query += filterParams.query
  if (filterParams.categories) params['categories'] = filterParams.categories
  // add search-api config stuff
  const config = getSearchConfig(params)
  return axios.get<SearchResponseI>('businesses/search/facets', config)
    .then(response => {
      const data: SearchResponseI = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      let category = ErrorCategories.SEARCH
      if (error?.response?.status === StatusCodes.SERVICE_UNAVAILABLE) category = ErrorCategories.SEARCH_UNAVAILABLE
      return {
        searchResults: null,
        error: {
          statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
          message: error?.response?.data?.message,
          category: category,
          type: error?.parsed?.rootCause?.type
        }
      }
    })
}

export async function searchParties(
  searchValue: string,
  filters: SearchPartyFilterI,
  rows: number,
  start: number
): Promise<SearchResponseI> {
  if (!searchValue) return

  // basic params
  const params = {
    query: `value:${searchValue}`,
    categories: 'partyRoles:partner,proprietor',
    start: start * rows,
    rows: rows
  }
  // add filters
  const filterParams = addSearchPartyFilters(filters)
  if (filterParams.query) params.query += filterParams.query
  if (filterParams.categories) params.categories = filterParams.categories
  // add search-api config stuff
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

  headerInfo.waiveFees = headerInfo.option === StaffPaymentOptions.NO_FEE

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
          category: ErrorCategories.DOCUMENT_ACCESS_REQUEST_CREATE,
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
          category: ErrorCategories.DOCUMENT_ACCESS_REQUEST_HISTORY,
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
          category: ErrorCategories.REPORT_GENERATION,
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
          category: ErrorCategories.REPORT_GENERATION,
          type: error?.parsed?.rootCause?.type || ErrorCodes.SERVICE_UNAVAILABLE
        }
      }
    })
}
