import { ErrorI } from '@/interfaces'
import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'

// UI models

export interface SearchI {
  results: (SearchResultI | SearchPartyResultI)[]
  searchType: 'business' | 'partner'
  totalResults: number
  _error: ErrorI
  _loading: boolean
  _value: string
}

export interface SearchResultI {
  name: string
  identifier: string
  bn: string
  status: BusinessStatuses
  legalType: BusinessTypes | CorpTypeCd
}

export interface SearchPartyResultI {
  parentBN: string
  parentIdentifier: string
  parentLegalType: BusinessTypes | CorpTypeCd
  parentName: string
  parentStatus: BusinessStatuses
  partyName: string
  partyRoles: string[]
  partyType: 'person' | 'organization'
}

// api responses
export interface SearchResponseI {
  searchResults: {
    results: (SearchResultI | SearchPartyResultI)[]
    totalResults: number
  }
  error?: ErrorI
}
