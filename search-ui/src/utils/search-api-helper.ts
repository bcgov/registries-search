/* eslint-disable no-useless-constructor */
// Libraries
import { axios } from '@/utils'

// Interfaces
import { AutoCompleteResponseIF } from '@/interfaces'

//const HttpStatus = require('http-status-codes')

export async function getAutoComplete (searchValue: string): Promise<any> {
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

export async function searchBusiness (searchValue: string): Promise<any> {
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

const mockSearchResponse = {
    "results" : [
       
    {'name':'LA-LA CREATIONS', 'identifier': 'CP7654321', 
    'bn': '1234567895', 'type': 'CP', 'status': 'Active'},

    
    {'name':'LA LA CONSTRUCTION', 'identifier': 'BC1218846', 
    'bn': '1234567895', 'type': 'BC', 'status': 'Active'},

    
    {'name':'BREW-LA-LA', 'identifier': 'CP1252646', 
    'bn': '1234567895', 'type': 'CP', 'status': 'Historical'},

    
    {'name':'SHOE LA LA', 'identifier': 'FM1218846', 
    'bn': '1234567895', 'type': 'SP', 'status': 'Active'}

]}

const mockAutoCompleteResponse = {
    "total":10,
    "first_index":1,
    "last_index":10,
    "results":[
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"LA LA CONSTRUCTION",
          "topic_source_id":"FM0601236",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"9e24c454-4fed-4c58-a741-381da5e0f66e",
          "score":46.695248
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"BREW-LA-LA",
          "topic_source_id":"FM0680287",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"79129398-f53f-45ca-a1f3-a8f1a44118b6",
          "score":46.695248
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"SHOE LA LA",
          "topic_source_id":"FM0586238",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"fbf04c92-b42d-4b1c-929a-05ddf3e8f59c",
          "score":46.695248
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"LA-LA CREATIONS",
          "topic_source_id":"FM0274353",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"32ba0bff-f55f-4a17-8bb8-9162c3cbd20f",
          "score":46.695248
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"SHOE LA LA",
          "topic_source_id":"FM0611664",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"4a101b3f-6589-4fe1-bd3c-454f192b8911",
          "score":46.695248
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"LA LA LA WORLD PRODUCTIONS INC.",
          "topic_source_id":"BC0591216",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"a0babc47-3c86-4f85-84d9-04a9495bf51e",
          "score":44.072617
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"LA LA LA AROMATIC BATHING COMPANY",
          "topic_source_id":"FM0185987",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"414be621-42bb-4193-94af-0702960005ee",
          "score":44.072617
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"LA LA LAND ENTERPRISES",
          "topic_source_id":"FM0359531",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"9986573b-8b77-4b3e-8cc7-d12980442ac0",
          "score":43.031013
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"OH LA LA FASHIONS",
          "topic_source_id":"FM0074395",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"ae1108e3-a6f4-457d-a89a-49fb3a9c3437",
          "score":42.794243
       },
       {
          "type":"name",
          "sub_type":"entity_name",
          "value":"MOO LA LA MUSIC",
          "topic_source_id":"FM0324729",
          "topic_type":"registration.registries.ca",
          "credential_type":"registration.registries.ca",
          "credential_id":"eec213e1-ec71-4813-8258-0606a404d124",
          "score":42.794243
       }
    ]
 }
