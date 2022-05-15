import { ErrorI } from '@/interfaces'
import { BusinessStatuses, BusinessTypes } from '@/enums'

export interface SearchResponseI {     
    results: Array<SearchResultI>
    error?: ErrorI
}
 
export interface SearchResultI {
    legal_name: string
    identifier: string
    bn: string
    state:BusinessStatuses
    legal_type: BusinessTypes
}