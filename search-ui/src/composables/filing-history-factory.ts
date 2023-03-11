import { computed, reactive } from 'vue'

import { ApiFiling } from '@/interfaces/legal-api-responses'
import { getFilings } from '@/requests'
import { FilingI } from '@/interfaces'


const filingHistory = reactive({
    filings: [] as ApiFiling[],
    latestFiling: null,
    _effective_date: '',
    _error: null,
    _identifier: '',
    _loading: false
}) as FilingI

export const useFilingHistory = () => {
    // functions  to manage the filing history
    const clearFilingHistory = () => {
        filingHistory._effective_date = null
        filingHistory._error = null
        filingHistory._identifier = ''
        filingHistory.filings = []
        filingHistory.latestFiling = null
    }


    const loadFilingHistory = async (identifier: string, effective_date: string) => {
        filingHistory._loading = true
        clearFilingHistory()
        filingHistory._identifier = identifier
        filingHistory._effective_date = effective_date
        const filingsResp = await getFilings(identifier, effective_date)
        if (effective_date) {
            const all_filings = await getFilings(identifier, null)
            if (!all_filings.error) {                 
                filingHistory.latestFiling = all_filings[0]
            }
        }
        if (filingsResp.error) {
            filingHistory._error = filingsResp.error
        } else {
            filingHistory.filings = filingsResp.filings
        }
        filingHistory._loading = false
    }

    const hasCourtOrderFilings = computed(() => filingHistory.filings.filter(
        filing => filing.displayName == 'Court Order').length > 0)

    return {
        filingHistory,
        clearFilingHistory,
        loadFilingHistory,
        hasCourtOrderFilings
    }
}
