import { reactive } from 'vue'
// local
import { SearchI } from '@/interfaces'
import { searchBusiness } from '@/requests'

const search = reactive({
  results: null,
  _error: null,
  _loading: false,
  _value: '', // not used for anything yet
} as SearchI)

export const useSearch = () => {
  const getSearchResults = async (val: string) => {
    search._loading = true
    search._value = val
    const searchResp = await searchBusiness(val)
    if (searchResp) {
      if (searchResp.error) {
        search.results = []
        search._error = searchResp.error
      } else {
        search.results = searchResp.searchResults.results
      }
    } else {
      search.results = []
      console.error('Nothing returned from searchBusiness fn.')
    }
    search._loading = false
  }
  return {
    search,
    getSearchResults
  }
}