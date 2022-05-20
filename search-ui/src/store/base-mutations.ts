import { BaseStateI } from '@/interfaces'
import { ApiFiling } from '@/types'

export const mutateAuthRoles = (state: BaseStateI, authRoles: string[]) => {
  state.authorization.authRoles = authRoles
}

export const mutateSearchResults = (state: BaseStateI, searchResults: []) => {
  state.searchResults = searchResults
}

export const mutateFilings = (state: BaseStateI, filings: ApiFiling[]) => {
  state.filings = filings
}
