import { ComputedRef } from 'vue'
import { AccountStatus, AccountType } from '@/enums'
import { ErrorI } from './error'

export interface AuthI {
  currentAccount: CurrentAccountI
  _error: ComputedRef<ErrorI>
  _tokenInitialized: ComputedRef<boolean>
}

export interface CurrentAccountI {
  accountStatus: AccountStatus
  accountType: AccountType
  id: number
  label: string
  name?: string  // currently added from jwt
  productSettings: string
  type: string
  urlorigin: string
  urlpath: string
}