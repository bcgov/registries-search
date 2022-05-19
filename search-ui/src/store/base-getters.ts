import { BaseStateI } from '@/interfaces'

export const getUserRoles = (state: BaseStateI): string[] => {
  return state.authorization?.authRoles
}

export const getSearchResults = (state: BaseStateI): [] => {
  return state.searchResults
}

/** Is True if Staff role is set. */
export const isRoleStaff = (state: BaseStateI): boolean {
  return state.authorization.authRoles.includes('staff')
},

