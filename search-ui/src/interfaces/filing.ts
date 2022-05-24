import { ErrorI } from '@/interfaces'
import { ApiFiling } from '@/types'

export interface FilingI {
    filings: ApiFiling[],
    _error: ErrorI,
    _loading: boolean,
}