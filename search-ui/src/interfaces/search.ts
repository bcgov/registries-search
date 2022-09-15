import { ErrorI } from '@/interfaces'
import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'

// UI models

export interface SearchI {
  filters: SearchFilterI | SearchPartyFilterI
  results: (SearchResultI | SearchPartyResultI)[]
  searchType: 'business' | 'partner'
  totalResults: number
  unavailable: boolean
  _error: ErrorI
  _loading: boolean
  _loadingNext: boolean
  _start: number,
  _value: string
}

export interface SearchFilterI {
  name: string
  identifier: string
  bn: string
  status: BusinessStatuses.ACTIVE | BusinessStatuses.HISTORICAL
  legalType: BusinessTypes | CorpTypeCd
}

export interface SearchPartyFilterI {
  parentBN: string
  parentIdentifier: string
  parentName: string
  parentStatus: BusinessStatuses.ACTIVE | BusinessStatuses.HISTORICAL
  partyName: string
  partyRoles: 'partner' | 'proprietor'
}

export interface SearchResultI {
  name: string
  identifier: string
  bn: string
  status: BusinessStatuses.ACTIVE | BusinessStatuses.HISTORICAL
  legalType: BusinessTypes | CorpTypeCd
}

export interface SearchPartyResultI {
  parentBN: string
  parentIdentifier: string
  parentLegalType: BusinessTypes | CorpTypeCd
  parentName: string
  parentStatus: BusinessStatuses.ACTIVE | BusinessStatuses.HISTORICAL
  partyName: string
  partyRoles: string[]
  partyType: 'person' | 'organization'
}

// api responses
export interface SearchResponseI {
  searchResults: {
    queryInfo: { query: { value: string } } // partial def (other parts not used)
    results: (SearchResultI | SearchPartyResultI)[]
    totalResults: number
  }
  error?: ErrorI
}
