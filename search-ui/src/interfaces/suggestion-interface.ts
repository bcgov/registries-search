import { SuggestionTypes } from '@/enums'
import { ErrorI } from '@/interfaces'

export interface SuggestionResponseI {     
    results: Array<SuggestionI>,
    error?: ErrorI
}
 
export interface SuggestionI {
    type: SuggestionTypes
    value: string
}