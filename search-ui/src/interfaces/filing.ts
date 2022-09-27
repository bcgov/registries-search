import { ErrorI } from '@/interfaces'
import { ApiFiling } from '@/interfaces/legal-api-responses'

export interface FilingI {
    filings: ApiFiling[],
    latestFiling: ApiFiling,
    _effective_date: string,
    _error: ErrorI,
    _identifier: string,
    _loading: boolean,
}