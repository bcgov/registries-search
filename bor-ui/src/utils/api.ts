import { StatusCodes } from 'http-status-codes'
// internal
import type { ErrorCategoryE, ErrorCodeE } from '#imports'

export const getApiConfig = (url: string, apiKey: string, pdfDownload: boolean, params?: any) => {
  if (!url) { console.error('Error: API URL expected, but not given.') }
  if (!apiKey) { console.error('Error: API KEY expected, but not given.') }

  const config: any = { baseURL: url, headers: { 'x-apikey': apiKey }, params }
  if (pdfDownload) {
    config.headers.Accept = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    config.responseType = 'blob'
  }
  return config
}

export const parseGatewayError = (category: ErrorCategoryE, defaultStatus: StatusCodes, error): ErrorI => {
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
  if (error.value?.data?.rootCause) { rootCause = parseRootCause(error.value.data.rootCause) }
  return {
    category,
    detail: rootCause?.detail || error?.response?.data?.detail,
    message: rootCause?.message || error?.response?.data?.message,
    statusCode: rootCause?.statusCode || error?.response?.status || defaultStatus,
    type: rootCause?.type?.trim() as ErrorCodeE
  }
}
