import { axios } from '@/utils'

// Interfaces
import { SearchResponseI, SuggestionResponseI } from '@/interfaces'
import { BusinessStatuses, BusinessTypes, SuggestionTypes } from '@/enums'

//const HttpStatus = require('http-status-codes')

export async function getAutoComplete(searchValue: string): Promise<any> {
  if (!searchValue) return
  return mockAutoCompleteResponse
  /*const url = sessionStorage.getItem('SEARCH_API_URL')
  const config = { baseURL: url }
  return axios.get<AutoCompleteResponseIF>(`search/autocomplete?q=${searchValue}`, config)
    .then(response => {
      const data = response?.data
      if (!data) {
        throw new Error('Invalid API response')
      }
      return data
    }).catch(error => {
      return error
    })*/
}

export async function searchBusiness(searchValue: string): Promise<any> {
  if (!searchValue) return
  return mockSearchResponse
  /*const url = sessionStorage.getItem('SEARCH_API_URL')
   const config = { baseURL: url }
   return axios.get<AutoCompleteResponseIF>(`search/autocomplete?q=${searchValue}`, config)
     .then(response => {
       const data = response?.data
       if (!data) {
         throw new Error('Invalid API response')
       }
       return data
     }).catch(error => {
       return error
     })*/
}

const mockSearchResponse: SearchResponseI = {
  results: [
    {
      name: 'LA-LA CREATIONS',
      identifier: 'CP7654321',
      bn: '1234567895',
      type: BusinessTypes.COOPERATIVE_ASSOCIATION,
      status: BusinessStatuses.ACTIVE
    },

    {
      name: 'LA LA CONSTRUCTION',
      identifier: 'BC1218846',
      bn: '1234567895',
      type: BusinessTypes.BC_LIMITED_COMPANY,
      status: BusinessStatuses.ACTIVE
    },

    {
      name: 'BREW-LA-LA',
      identifier: 'CP1252646',
      bn: '1234567895',
      type: BusinessTypes.COOPERATIVE_ASSOCIATION,
      status: BusinessStatuses.HISTORICAL
    },

    {
      name: 'SHOE LA LA',
      identifier: 'FM1218846',
      bn: '1234567895',
      type: BusinessTypes.SOLE_PROPRIETOR,
      status: BusinessStatuses.ACTIVE
    }
  ]
}

const mockAutoCompleteResponse: SuggestionResponseI = {
  results: [
    {
      type: SuggestionTypes.NAME,
      value: '<b>LA LA</b> CONSTRUCTION'
    },
    {
      type: SuggestionTypes.NAME,
      value: 'BREW-<b>LA-LA</b>'
    },
    {
      type: SuggestionTypes.NAME,
      value: '<b>LA-LA</b> CREATIONS'
    },
    {
      type: SuggestionTypes.NAME,
      value: 'SHOE <b>LA LA</b>'
    },
    {
      type: SuggestionTypes.NAME,
      value: '<b>LA LA</b> LA WORLD PRODUCTIONS INC.'
    },
    {
      type: SuggestionTypes.NAME,
      value: '<b>LA LA</b> LA AROMATIC BATHING COMPANY'
    },
    {
      type: SuggestionTypes.NAME,
      value: 'LA LA LAND ENTERPRISES'
    },
    {
      type: SuggestionTypes.NAME,
      value: 'OH LA LA FASHIONS'
    },
    {
      type: SuggestionTypes.NAME,
      value: 'MOO LA LA MUSIC'
    },
    {
      type: SuggestionTypes.NAME,
      value: 'LA LA BAND'
    }
  ]
}
