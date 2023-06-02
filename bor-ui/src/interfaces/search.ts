// external
import { ComputedRef } from 'vue'
// internal
import { AddressI, ErrorI } from '@/interfaces'
import { BusinessState, CorpTypeCd, EntityType, RoleType } from '@/enums'

// UI models

export interface SearchI {
  facetsResult: FacetsResultI
  filters: SearchPayloadI
  results: SearchResultI[]
  totalResults: number
  unavailable: boolean
  _error: ComputedRef<ErrorI>
  _isFilteringActive: ComputedRef<boolean>
  _loading: ComputedRef<boolean>
  _loadingNext: ComputedRef<boolean>
  _start: ComputedRef<number>,
  _value: ComputedRef<string>
}

export interface SearchResultI {
  bn?: string
  entityAddresses: AddressI[]
  entityType: 'BUSINESS' | 'PERSON'
  legalName: string
  legalType?: CorpTypeCd
  identifier?: string
  roles: {
    active: boolean
    relatedBN?: string
    relatedEntityType: 'BUSINESS' | 'PERSON'
    relatedIdentifier: string
    relatedName: string
    relatedState: BusinessState
    roleDates: { end?: Date, start: Date }[]
    roleType: RoleType
  }[],
  state?: BusinessState
}

export interface SearchResponseI {
  facets: FacetsResultI
  searchResults: {
    queryInfo: { query: { value: string } } // partial def (other parts not used)
    results: SearchResultI[]
    totalResults: number
  }
  error?: ErrorI
}

export interface SearchPayloadI {
  query: {
    bn?: string
    entityAddresses?: string
    identifier?: string
    legalName?: string
    roles: {
      relatedBN?: string
      relatedIdentifier?: string
      relatedName?: string
      roleDates?: { start?: string, end?: string }  // ISO strings. Can be partial (i.e. 2023-10) or full datetime
      value?: string  // will match on related bn/identifer/name (creates 'or' clauses for all 3 fields)
    }
    value?: string
  }
  categories: {
    entityType?: EntityType[]
    legalType?: CorpTypeCd[]
    roles: {
      relatedEntityType?: EntityType[]
      relatedState?: BusinessState[]
      roleType?: RoleType[]
    }
    state?: BusinessState[]
  }
  rows?: number
  start?: number
}

export interface FacetI {
  count: number
  parentCount?: number
  value: string
}

export interface FacetsResultI {
  fields?: {
    entityType: FacetI[]
    legalType: FacetI[]
    relatedEntityType: FacetI[]
    relatedLegalType: FacetI[]
    relatedState: FacetI[]
    roleType: FacetI[]
    state: FacetI[]
  }
}
