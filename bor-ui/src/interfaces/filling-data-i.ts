export interface FilingDataI {
  filingDescription?: string
  filingTypeCode: string
  entityType: string
  waiveFees: boolean
  priority: boolean
  futureEffective: boolean
}

export interface PayFeesApiQueryParamsI {
  waiveFees?: boolean
  priority?: boolean
  futureEffective?: boolean
}
