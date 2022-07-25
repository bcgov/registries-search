import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
import { ActionComps, FeeEntities } from '@/enums'
import { FeeCodes } from '@/enums/fee-codes'
import { ErrorI } from '@/interfaces'
import { ComputedRef } from 'vue'

export interface FeeI {
  code: FeeCodes
  fee: number
  label: string
  quantity: number
  serviceFee: number
}

export interface FeeDataI {
  entityType: FeeEntities
  filingDescription?: string
  filingTypeCode: FeeCodes
  futureEffective?: boolean
  priority?: boolean
  waiveFees?: boolean
}

export interface FeesI {
  folioNumber: string
  items: Array<FeeI>
  preSelection: FeeI
  staffPaymentData: StaffPaymentIF
  _error: ErrorI
}

export type CachedFeeItem = {
  [key in FeeCodes]?: FeeI
}

export type FeeAction = {
  action: (val?: string) => any
  compType: ActionComps
  iconLeft?: string
  iconRight?: string
  text: string
  outlined: boolean,
  disabled?: ComputedRef<boolean>
}