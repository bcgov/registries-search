import { ActionI } from '@/interfaces'

export const setAuthRoles: ActionI = ({ commit }, authRoles: string[]): void => {
  commit('mutateAuthRoles', authRoles)
}
