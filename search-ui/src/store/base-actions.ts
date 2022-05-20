import { ActionI } from '@/interfaces'
import {searchBusiness, getFilings} from '@/requests'
import { ApiFiling } from '@/types'
import { APIDetails } from '@sentry/core'

export const setAuthRoles: ActionI = ({ commit },authRoles: string[]): void => {
  commit('mutateAuthRoles', authRoles)
}

export const search: ActionI = async ({ commit }, searchString: string) => {
  commit('mutateSearchResults', [])
  const searchResults = await searchBusiness(searchString)   
  commit('mutateSearchResults', searchResults.results)
}

export const fetchFilings: ActionI = async ({ commit }, identifier: string) => {
  commit('mutateFilings', [])
  const filings: ApiFiling[] = await getFilings(identifier)
  commit('mutateFilings', filings)
}