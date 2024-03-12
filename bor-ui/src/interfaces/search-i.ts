export interface SearchResultI {
  bn?: string
  entityAddresses: AddressI[]
  entityType: 'BUSINESS' | 'PERSON'
  legalName: string
  legalType?: CorpTypeCdE
  identifier?: string
  roles: {
    active: boolean
    relatedBN?: string
    relatedEmail?: string
    relatedEntityType: 'BUSINESS' | 'PERSON'
    relatedIdentifier: string
    relatedLegalType: CorpTypeCdE
    relatedName: string
    relatedState: BusinessStateE
    roleDates: { end?: Date, start: Date }[]
    roleType: RoleTypeE
  }[],
  state?: BusinessStateE
}

export interface SearchPayloadI {
  query: {
    bn?: string
    entityAddresses?: string
    identifier?: string
    legalName?: string
    roles: {
      relatedBN?: string
      relatedEmail?: string
      relatedIdentifier?: string
      relatedName?: string
      roleDates?: { start?: string, end?: string } // ISO strings. Can be partial (i.e. 2023-10) or full datetime
      value?: string // will match on related bn/identifer/name (creates 'or' clauses for all 3 fields)
    }
    value?: string
  }
  categories: {
    entityType?: EntityTypeE[]
    legalType?: CorpTypeCdE[]
    roles: {
      relatedEntityType?: EntityTypeE[]
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
