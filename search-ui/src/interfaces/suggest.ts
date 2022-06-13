import { ErrorI } from '@/interfaces'
import { SuggestionTypes } from '@/enums'

// UI models
export interface SuggestI {
    disabled: boolean
    results: SuggestResultI[]
    query: string
    _error: ErrorI
    _loading: boolean
}

export interface SuggestResultI {
    type: SuggestionTypes
    value: string
}

// api responses
export interface SuggestionResponseI {     
    results: Array<SuggestResultI>,
    error?: ErrorI
}
