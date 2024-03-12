export interface TaxI {
  gst: number,
  pst: number
}

export interface FeeInfoI {
  filingFees: number,
  filingType: string,
  filingTypeCode: string,
  futureEffectiveFees: number,
  priorityFees: number,
  processingFees: number,
  serviceFees: number,
  tax: TaxI,
  total: number
}

export interface PayFeesWidgetItemI extends FeeInfoI {
  uiUuid: string,
  quantity?: number
}
