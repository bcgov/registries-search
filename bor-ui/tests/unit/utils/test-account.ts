import { AccountStatus, AccountTypes } from '@/enums'
import { CurrentAccountI } from '@/interfaces'

export const testAccount: CurrentAccountI = {
  accountStatus: AccountStatus.ACTIVE,
  accountType: AccountTypes.PREMIUM,
  id: 1234,
  label: 'Test Label',
  name: 'Test Account',
  productSettings: '',
  type: '',
  urlorigin: '',
  urlpath: ''
}