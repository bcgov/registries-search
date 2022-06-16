import { StatusCodes } from 'http-status-codes'
// local
import { ErrorCategories, ErrorCodes } from '@/enums'
import { CommentIF, EntityRespI } from '@/interfaces' 
import { axios } from '@/utils'

export async function getEntity(identifier: string): Promise<EntityRespI> {
  const url = sessionStorage.getItem('LEGAL_API_URL')
  if (!url) console.error('Error: LEGAL_API_URL expected, but not found.')
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
