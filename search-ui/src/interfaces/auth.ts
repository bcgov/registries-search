import { AccountStatus, AccountTypes, StaffRoles, UserRoles } from '@/enums'
import { AuthApiProductI } from './auth-api-responses'
import { ErrorI } from './error'

export interface AuthI {
  activeProducts: AuthApiProductI[]
  currentAccount: CurrentAccountI
  staffRoles: StaffRoles[]
  tokenInitialized: boolean
  userRoles: UserRoles[]
  _error: ErrorI
}

export interface CurrentAccountI {
  accountStatus: AccountStatus
  accountType: AccountTypes
  id: number
  label: string
  name?: string  // currently added from jwt
  productSettings: string
  type: string
  urlorigin: string
  urlpath: string
}