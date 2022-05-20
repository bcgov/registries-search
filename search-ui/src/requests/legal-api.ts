import { StatusCodes } from 'http-status-codes'
// local
import { ErrorCategories, ErrorCodes } from '@/enums'
import { axios } from '@/utils'

export async function getEntity(identifier: string): Promise<any> {
  const url = sessionStorage.getItem('LEGAL_API_URL')
  const config = { baseURL: url }
  return axios.get<any>(`businesses/${identifier}`, config)
    .then(response => {
      const data = response?.data
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
