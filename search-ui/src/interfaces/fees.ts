import { ActionComps } from '@/enums'
import { FeeCodes } from '@/enums/fee-codes'
import { ErrorI } from '@/interfaces'

export interface FeeI {
  code: FeeCodes
  fee: number
  label: string
  quantity: number
  serviceFee: number
}

export interface FeesI {
  folioNumber: string,
  items: Array<FeeI>
  preSelection: FeeI
  _error: ErrorI
}

export type CachedFeeItem = {
  [key in FeeCodes]: FeeI
}

export type FeeAction = {
  action: (val?: string) => any
  compType: ActionComps
  iconLeft?: string
  iconRight?: string
  text: string
  outlined: boolean
}