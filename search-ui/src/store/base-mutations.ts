import { BaseStateI } from '@/interfaces'

export const mutateAuthRoles = (state: BaseStateI, authRoles: string[]) => {
  state.authorization.authRoles = authRoles
}

export const mutateSearchResults = (state: BaseStateI, searchResults: []) => {
  state.searchResults = searchResults
}
