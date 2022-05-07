import { BaseStateI } from '@/interfaces'

export const getUserRoles = (state: BaseStateI): string[] => {
  return state.authorization?.authRoles
}

export const getSearchResults = (state: BaseStateI): [] => {
  return state.searchResults
}
