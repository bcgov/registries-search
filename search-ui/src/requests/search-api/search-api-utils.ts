import { StatusCodes } from 'http-status-codes'
// local
import { useAuth } from '@/composables'
import { CorpTypeCd, ErrorCategories, ErrorCodes } from '@/enums'
import { ErrorI, SearchFilterI, SearchPartyFilterI } from '@/interfaces'
import { OtherCorpTypes } from '@/resources'

export const addSearchBusFilters = (filters: SearchFilterI) => {
  const filterParams = { query: '', categories: '' }
  // filters
  if (filters?.bn) filterParams.query += `::bn:${filters.bn}`
  if (filters?.identifier) filterParams.query += `::identifier:${filters.identifier}`
  if (filters?.name) filterParams.query += `::name:${filters.name}`
  // categories
  if (filters?.legalType) {
    // group specific corp types together
    if (filters.legalType === 'Other' as CorpTypeCd) {
      // query by all 'other' corp types
      filters.legalType = OtherCorpTypes.join(',') as CorpTypeCd
    } else {
      const bcLimitedTypes = [CorpTypeCd.CONTINUE_IN, CorpTypeCd.BC_COMPANY]
      const ulcTypes = [CorpTypeCd.ULC_CONTINUE_IN, CorpTypeCd.BC_ULC_COMPANY]
      const societyTypes = [CorpTypeCd.CONT_IN_SOCIETY, CorpTypeCd.SOCIETY, CorpTypeCd.SOCIETY_BRANCH]
      const corp_grps = [bcLimitedTypes, ulcTypes, societyTypes]
      for (const i in corp_grps) {
        if (corp_grps[i].includes(filters.legalType as CorpTypeCd)) {
          // query by all society corp types
          filters.legalType = corp_grps[i].join(',') as CorpTypeCd
          break
        }
      }
    }
    filterParams.categories += `legalType:${filters.legalType}`
  }
  if (filters?.status) {
    filterParams.categories += filters?.legalType ? `::` : ''
    filterParams.categories += `status:${filters.status}`
  }
  return filterParams
}

export const addSearchPartyFilters = (filters: SearchPartyFilterI) => {
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

export const getSearchConfig = (params: object = null) => {
  const { auth } = useAuth()
  const url = sessionStorage.getItem('REGISTRY_SEARCH_API_URL')
  const apiKey = window['searchApiKey']
  if (!url) console.error('Error: REGISTRY_SEARCH_API_URL expected, but not found.')
  if (!apiKey) console.error('Error: REGISTRY_SEARCH_API_KEY expected, but not found.')
  if (!auth.currentAccount) console.error(`Error: current account expected, but not found.`)
  
  return { baseURL: url, headers: { 'Account-Id': auth.currentAccount?.id, 'x-apikey': apiKey }, params: params }
}

export const parseGatewayError = (category: ErrorCategories, defaultStatus: StatusCodes, error): ErrorI => {
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
    type: rootCause?.type?.trim() as ErrorCodes
  }
}
