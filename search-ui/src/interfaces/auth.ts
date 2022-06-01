import { AccountStatus, AccountTypes, StaffRoles } from '@/enums'
import { AuthApiProductI } from './auth-api-responses'
import { ErrorI } from './error'

export interface AuthI {
  activeProducts: AuthApiProductI[]
  currentAccount: CurrentAccountI
  staffRoles: StaffRoles[]
  tokenInitialized: boolean
  _error: ErrorI
}

export interface CurrentAccountI {
  accountStatus: AccountStatus
  accountType: AccountTypes
  id: number
  label: string
  productSettings: string
  type: string
  urlorigin: string
  urlpath: string
}