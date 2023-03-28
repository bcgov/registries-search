import { AccountStatus, AccountType } from '@/enums'
import { CurrentAccountI } from '@/interfaces'

export const testAccount: CurrentAccountI = {
  accountStatus: AccountStatus.ACTIVE,
  accountType: AccountType.PREMIUM,
  id: 1234,
  label: 'Test Label',
  name: 'Test Account',
  productSettings: '',
  type: '',
  urlorigin: '',
  urlpath: ''
}