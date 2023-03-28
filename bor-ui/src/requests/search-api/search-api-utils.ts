import { StatusCodes } from 'http-status-codes'
// local
import { useAuth } from '@/composables'
import { ErrorCategory, ErrorCode } from '@/enums'
import { ErrorI } from '@/interfaces'

export const getSearchConfig = () => {
  const { auth } = useAuth()
  const url = sessionStorage.getItem('BOR_API_URL')
  const apiKey = window['borApiKey']
  if (!url) console.error('Error: BOR_API_URL expected, but not found.')
  if (!apiKey) console.error('Error: BOR_API_KEY expected, but not found.')
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)
  
  return { baseURL: url, headers: { 'Account-Id': auth.currentAccount?.id, 'x-apikey': apiKey } }
}

export const parseGatewayError = (category: ErrorCategory, defaultStatus: StatusCodes, error): ErrorI => {
  const parseRootCause = (rootCause: string) => {
    try {
      let parsedRootCause = rootCause.replace('detail:', '"detail":"')
        .replace('type:', '"type":"')
        .replace('message:', '"message":"')
        .replace('status_code:', '"statusCode":"')
        .replaceAll(',', '",')
      parsedRootCause = `{${parsedRootCause}"}`
      return JSON.parse(parsedRootCause)
    } catch (error) {
      console.warn(error)
      return null
    }
  }
  // parse root cause
  let rootCause = null
  if (error?.response?.data?.rootCause) rootCause = parseRootCause(error.response.data.rootCause)
  return {
    category: category,
    detail: rootCause?.detail || error?.response?.data?.detail,
    message: rootCause?.message || error?.response?.data?.message,
    statusCode: rootCause?.statusCode || error?.response?.status || defaultStatus,
    type: rootCause?.type?.trim() as ErrorCode
  }
}
