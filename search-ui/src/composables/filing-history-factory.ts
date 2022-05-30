import { reactive } from 'vue'

import { ApiFiling } from '@/interfaces/legal-api-responses'
import { getFilings } from '@/requests'
import { FilingI } from '@/interfaces'


const filingHistory = reactive({
    filings: [] as ApiFiling[],
    _error: null,
    _loading: false
}) as FilingI

export const useFilingHistory = () => {
    // functions  to manage the filing history
    const clearFilingHistory = () => {
        filingHistory._error = null
        filingHistory.filings = []
    }


    const loadFilingHistory = async (identifier: string) => {
        filingHistory._loading = true
        clearFilingHistory()
        const filings = await getFilings(identifier)
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
