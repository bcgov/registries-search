import type { BusinessStateE, BusinessTypeE } from '#imports'

export interface RegSearchPayloadI {
  query: {
    value?: string
    name?: string
    identifier?: string
    bn?: string
    parties?: { partyName: string }
  }
  categories: {
    status?: BusinessStateE[]
    legalType?: BusinessTypeE[]
  },
  rows?: number
  start?: number
}

export interface RegSearchResultI {
  name: string
  identifier: string
  bn: string
  status: BusinessStateE.ACTIVE | BusinessStateE.HISTORICAL
  legalType: BusinessTypeE
}

// api responses
export interface RegSearchResponseI {
  facets?: FacetsResultI
  searchResults: {
    queryInfo: RegSearchPayloadI
    results: RegSearchResultI[]
    totalResults: number
  }
  error?: ErrorI
}
