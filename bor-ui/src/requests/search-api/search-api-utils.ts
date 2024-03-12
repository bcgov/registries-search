import { StatusCodes } from 'http-status-codes'

export const getSearchConfig = (exportSearch: boolean) => {
  const { borApiURL, borApiKey } = useRuntimeConfig().public
  if (!borApiURL) { console.error('Error: BOR_API_URL expected, but not found.') }
  if (!borApiKey) { console.error('Error: BOR_API_KEY expected, but not found.') }

  const account = useBcrosAccount()
  if (!account.currentAccount) { console.error('Error: current account expected, but not found.') }

  const config = { baseURL: borApiURL, headers: { 'Account-Id': account.currentAccount?.id, 'x-apikey': borApiKey } }
  if (exportSearch) {
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
  if (error?.response?.data?.rootCause) { rootCause = parseRootCause(error.response.data.rootCause) }
  return {
    category,
    detail: rootCause?.detail || error?.response?.data?.detail,
    message: rootCause?.message || error?.response?.data?.message,
    statusCode: rootCause?.statusCode || error?.response?.status || defaultStatus,
    type: rootCause?.type?.trim() as ErrorCodeE
  }
}
