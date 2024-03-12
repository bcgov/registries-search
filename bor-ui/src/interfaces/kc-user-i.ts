import { LoginSourceE } from '~/enums/login-source-e'

export interface KCUserI {
  firstName: string
  lastName: string
  fullName: string
  userName: string
  email: string
  keycloakGuid: string // sub
  loginSource: LoginSourceE
  roles: string[]
}
