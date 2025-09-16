export interface SearchResultRoleInterest {
  details: string
  endDate?: string
  interestType: PersonControlCategory
  otherReason?: string
  relatedParties?: { interestPartyID: string, interestPartyName: string }[]
  sharesExact?: number
  sharesMax?: number
  sharesMin?: number
  startDate: string
}

export interface SearchResultRole {
  active: boolean
  relatedAddresses?: Partial<Address>[]
  relatedBN?: string
  relatedEmail?: string
  relatedEntityType: 'BUSINESS' | 'PERSON'
  relatedIdentifier: string
  relatedLegalType: BusinessType
  relatedInterests?: SearchResultRoleInterest[]
  relatedName: string
  relatedState: BusinessState
  roleDates: { end?: string, start: string }[]
  roleType: SearchRoleType
}

export interface SearchResult {
  alternateName?: string
  birthDate?: string
  bn?: string
  email?: string
  entityAddresses: Partial<Address>[]
  entityType: 'BUSINESS' | 'PERSON'
  isPR?: boolean
  legalName: string
  legalType?: BusinessType
  identifier?: string
  nationalities?: string[]
  phoneNumber?: string
  roles: SearchResultRole[]
  state?: BusinessState
  taxNumber?: string
  taxResidencies?: string[]
}

export interface SearchPayload {
  query: {
    bn?: string
    entityAddresses?: string
    identifier?: string
    name?: string
    info?: string
    roles?: {
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
    entityType?: BusinessType[]
    legalType?: BusinessType[]
    nationalities?: string[]
    roles?: {
      relatedEntityType?: BusinessType[]
      relatedState?: BusinessState[]
      roleType?: SearchRoleType[]
    }
    state?: BusinessState[]
  }
  rows?: number
  start?: number
}

export interface Facet {
  count: number
  parentCount?: number
  value: string
  selected?: boolean
}

export interface FacetsResult {
  fields?: {
    entityType?: Facet[]
    legalType?: Facet[]
    relatedEntityType?: Facet[]
    relatedLegalType?: Facet[]
    relatedState?: Facet[]
    roleType?: Facet[]
    status?: Facet[]
    state?: Facet[]
  }
}

export interface SearchResponse {
  facets: FacetsResult
  searchResults: {
    queryInfo: { query: { value: string } } // partial def (other parts not used)
    results: SearchResult[]
    totalResults: number
  }
  error?: SearchError
}

export interface Search {
  exportRows: number
  facetsResult: FacetsResult
  filters: SearchPayload
  results: SearchResult[]
  totalResults: number
  _error: ComputedRef<SearchError>
  _isFilteringActive: ComputedRef<boolean>
  _loading: ComputedRef<boolean>
  _loadingNext: ComputedRef<boolean>
  _start: ComputedRef<number>
  _value: ComputedRef<string>
}
