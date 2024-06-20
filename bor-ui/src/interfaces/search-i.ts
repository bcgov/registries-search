import type { BusinessStateE, BusinessTypeE, PersonControlCategoryE, RoleTypeE } from '#imports'

export interface SearchResultRoleInterestI {
  details: string
  endDate?: string
  interestType: PersonControlCategoryE
  otherReason?: string
  relatedParties?: { interestPartyID: string, interestPartyName: string }[]
  sharesExact?: number
  sharesMax?: number
  sharesMin?: number
  startDate: string
}

export interface SearchResultRoleI {
  active: boolean
  relatedAddresses?: Partial<AddressI>[]
  relatedBN?: string
  relatedEmail?: string
  relatedEntityType: 'BUSINESS' | 'PERSON'
  relatedIdentifier: string
  relatedLegalType: BusinessTypeE
  relatedInterests?: SearchResultRoleInterestI[]
  relatedName: string
  relatedState: BusinessStateE
  roleDates: { end?: Date, start: Date }[]
  roleType: RoleTypeE
}

export interface SearchResultI {
  alternateName?: string,
  birthDate?: string,
  bn?: string,
  email?: string,
  entityAddresses: Partial<AddressI>[]
  entityType: 'BUSINESS' | 'PERSON'
  isPR?: boolean
  legalName: string
  legalType?: BusinessTypeE
  identifier?: string,
  nationalities?: string[]
  phoneNumber?: string
  roles: SearchResultRoleI[],
  state?: BusinessStateE,
  taxNumber?: string,
  taxResidencies?: string[]
}

export interface SearchPayloadI {
  query: {
    bn?: string
    entityAddresses?: string
    identifier?: string
    name?: string
    info?: string
    roles: {
      relatedBN?: string
      relatedEmail?: string
      relatedIdentifier?: string
      relatedInterests?: string[]
      relatedName?: string
      roleDates?: { start?: string, end?: string } // ISO strings. Can be partial (i.e. 2023-10) or full datetime
      value?: string // will match on related bn/identifer/name (creates 'or' clauses for all 3 fields)
    }
    value?: string
  }
  categories: {
    entityType?: BusinessTypeE[]
    legalType?: BusinessTypeE[]
    roles: {
      relatedEntityType?: BusinessTypeE[]
      relatedState?: BusinessStateE[]
      roleType?: RoleTypeE[]
    }
    state?: BusinessStateE[]
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

export interface SearchResponseI {
  facets: FacetsResultI
  searchResults: {
    queryInfo: { query: { value: string } } // partial def (other parts not used)
    results: SearchResultI[]
    totalResults: number
  }
  error?: ErrorI
}

export interface SearchI {
  exportRows: number
  facetsResult: FacetsResultI
  filters: SearchPayloadI
  results: SearchResultI[]
  totalResults: number
  _error: ComputedRef<ErrorI>
  _isFilteringActive: ComputedRef<boolean>
  _loading: ComputedRef<boolean>
  _loadingNext: ComputedRef<boolean>
  _start: ComputedRef<number>,
  _value: ComputedRef<string>
}
