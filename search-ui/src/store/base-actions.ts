import { ActionI } from '@/interfaces'
import { searchBusiness } from '@/requests'

export const setAuthRoles: ActionI = ({ commit }, authRoles: string[]): void => {
  commit('mutateAuthRoles', authRoles)
}

export const search: ActionI = async ({ commit }, searchString: string) => {
  commit('mutateSearchResults', [])
  const searchResults = await searchBusiness(searchString)
  commit('mutateSearchResults', searchResults.results)
}