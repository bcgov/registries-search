import { BaseStateI } from '@/interfaces'

export const mutateAuthRoles = (state: BaseStateI, authRoles: string[]) => {
  state.authorization.authRoles = authRoles
}
