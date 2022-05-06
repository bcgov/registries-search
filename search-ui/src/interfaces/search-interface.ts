import { ErrorI } from '@/interfaces'
import { BusinessStatuses, BusinessTypes } from '@/enums'

export interface SearchResponseI {     
    results: Array<SearchResultI>
    error?: ErrorI
}
 
export interface SearchResultI {
    name: string
    identifier: string
    bn: string
    status:BusinessStatuses
    type: BusinessTypes
}