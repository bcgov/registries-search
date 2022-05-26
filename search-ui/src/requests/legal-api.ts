import { StatusCodes } from 'http-status-codes'
// local
import { ErrorCategories, ErrorCodes } from '@/enums'
import { CommentIF } from '@/interfaces'
import { EntityRespI, ApiDocuments } from '@/interfaces/legal-api-responses'
import {  Document } from '@/types'
import { axios } from '@/utils'

export async function getEntity(identifier: string): Promise<EntityRespI> {
  const url = sessionStorage.getItem('LEGAL_API_URL')
  const config = { baseURL: url }
  return axios.get<any>(`businesses/${identifier}`, config)
    .then(response => {
      const data = response?.data
      if (!data) throw new Error('Invalid API response')
      if (!data.business) throw new Error('Expecting `business` in API response.')
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

export async function getFilings(identifier: string): Promise<any> {
  const url = sessionStorage.getItem('LEGAL_API_URL')
  const config = { baseURL: url }
  return axios.get<any>(`businesses/${identifier}/filings`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data?.filings || []
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
* Fetches documents object.
* @param url the full URL to fetch the documents
* @returns a promise to return the documents object from the response
*/
export const fetchDocuments = async (url: string): Promise<ApiDocuments> => {
  const config = { baseURL: sessionStorage.getItem('LEGAL_API_URL') }
  return axios.get<any>(`${url}`, config)
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
export const fetchDocument = (document: Document): Promise<any> => {
  // safety checks
  if (!document?.link || !document?.filename) {
    throw new Error('Invalid parameters')
  }

  const config = {
    headers: { 'Accept': 'application/pdf' },
    responseType: 'blob' as 'json'
  }

  return axios.get(document.link, config).then(response => {
    if (!response) throw new Error('Null response')

    /* solution from https://github.com/axios/axios/issues/1392 */

    // it is necessary to create a new blob object with mime-type explicitly set
    // otherwise only Chrome works like it should
    const blob = new Blob([response.data], { type: 'application/pdf' })

    // use Navigator.msSaveOrOpenBlob if available (possibly IE)
    // warning: this is now deprecated
    // ref: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/msSaveOrOpenBlob
    if (window.navigator && window.navigator['msSaveOrOpenBlob']) {
      window.navigator['msSaveOrOpenBlob'](blob, document.filename)
    } else {
      // for other browsers, create a link pointing to the ObjectURL containing the blob
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
  })
}

/**
 * Fetches comments array.
 * @param url the full URL to fetch the comments
 * @returns a promise to return the comments array from the response
 */
export const fetchComments = async (url: string): Promise<CommentIF[]> => {
  return axios.get(url)
    .then(response => {
      const comments = response?.data?.comments
      if (!comments) {
        // eslint-disable-next-line no-console
        console.log('fetchComments() error - invalid response =', response)
        throw new Error('Invalid API response')
      }
      return comments
    })
}
