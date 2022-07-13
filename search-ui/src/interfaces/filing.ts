import { ErrorI } from '@/interfaces'
import { ApiFiling } from '@/interfaces/legal-api-responses'

export interface FilingI {
    filings: ApiFiling[],
    latestFiling: ApiFiling,
    _error: ErrorI,
    _loading: boolean,
}