import type { BusinessStateE, BusinessTypeE } from '#imports'

export interface RegSearchFilterI {
  name: string
  identifier: string
  bn: string
  status: BusinessStateE.ACTIVE | BusinessStateE.HISTORICAL
  legalType: BusinessTypeE
}

export interface RegSearchResultI {
  name: string
  identifier: string
  bn: string
  status: BusinessStateE.ACTIVE | BusinessStateE.HISTORICAL
  legalType: BusinessTypeE
}

export interface RegSearchI {
  filters: RegSearchFilterI
  results: RegSearchResultI[]
  totalResults: number
  unavailable: boolean
  _error: ErrorI
  _loading: boolean
  _loadingNext: boolean
  _start: number,
  _value: string
}

// api responses
export interface RegSearchResponseI {
  facets?: FacetsResultI
  searchResults: {
    queryInfo: { query: { value: string } } // partial def (other parts not used)
    results: RegSearchResultI[]
    totalResults: number
  }
  error?: ErrorI
}
