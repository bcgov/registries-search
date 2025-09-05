export interface BusinessSearchPayload {
  query: {
    value?: string
    name?: string
    identifier?: string
    bn?: string
    parties?: { partyName: string }
  }
  categories: {
    status?: BusinessState[]
    legalType?: BusinessType[]
  }
  rows?: number
  start?: number
}

export interface BusinessSearchResult {
  name: string
  identifier: string
  bn: string
  status: BusinessState
  legalType: BusinessType
  goodstanding?: boolean
  modernized?: boolean
}

// api responses
export interface BusinessSearchResponse {
  facets?: FacetsResult
  searchResults: {
    queryInfo: BusinessSearchPayload
    results: BusinessSearchResult[]
    totalResults: number
  }
  error?: SearchError
}
