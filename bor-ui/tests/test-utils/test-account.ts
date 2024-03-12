// import { AccountStatusE } from '../../src/enums/account-status-e'
// import { AccountTypeE } from '../../src/enums/account-type-e'
// import { UserSettingsTypeE } from '../../src/enums/user-settings-type-e'
// import { AccountI } from '../../src/interfaces/account-i'

export const testAccount: AccountI = {
  accountStatus: AccountStatusE.ACTIVE,
  accountType: AccountTypeE.PREMIUM,
  id: '1234',
  label: 'Test Label',
  type: UserSettingsTypeE.ACCOUNT,
  urlorigin: '',
  urlpath: ''
}
