import { reactive } from 'vue'

import { ApiFiling } from '@/interfaces/legal-api-responses'
import { getFilings } from '@/requests'
import { FilingI } from '@/interfaces'


const filingHistory = reactive({
    filings: [] as ApiFiling[],
    latestFiling: null,
    _error: null,
    _loading: false
}) as FilingI

export const useFilingHistory = () => {
    // functions  to manage the filing history
    const clearFilingHistory = () => {
        filingHistory._error = null
        filingHistory.filings = []
        filingHistory.latestFiling = null
    }


    const loadFilingHistory = async (identifier: string, effective_date: string) => {
        filingHistory._loading = true
        clearFilingHistory()
        const filings = await getFilings(identifier, effective_date)
        if (effective_date) {
            const all_filings = await getFilings(identifier, null)
            if (!all_filings.error) {                 
                filingHistory.latestFiling = all_filings[0]
            }
        }
        if (filings.error) {
            filingHistory._error = filings.error
        }
        else {
            filingHistory.filings = filings
        }
        filingHistory._loading = false
    }

    return {
        filingHistory,
        clearFilingHistory,
        loadFilingHistory
    }
}
