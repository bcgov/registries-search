import type { StatusCodes } from 'http-status-codes'

export const getApiConfig = (pdfDownload: boolean, params?: any, overrideUrl?: string) => {
  const config: any = { headers: {}, params }
  if (pdfDownload) {
    config.headers.Accept = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    config.responseType = 'blob'
  }
  if (overrideUrl) {
    config.baseURL = overrideUrl
  }
  return config
}

export const parseGatewayError = (
  category: ErrorCategory,
  defaultStatus: StatusCodes,
  data: { errorMessage: string, rootCause: string }
): SearchError => {
  const parseRootCause = (rootCause: string) => {
    try {
      let parsedRootCause = rootCause.replace('detail:', '"detail":"')
        .replace('type:', '"type":"')
        .replace('message:', '"message":"')
        .replace('status_code:', '"statusCode":"')
        .replaceAll(' None,', '')
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
  if (data?.rootCause) {
    rootCause = parseRootCause(data.rootCause)
  }
  return {
    category,
    detail: rootCause?.detail,
    message: rootCause?.message || data.errorMessage,
    statusCode: rootCause?.statusCode || defaultStatus,
    type: rootCause?.type?.trim() as ErrorCode
  }
}
