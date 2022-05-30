import { computed, reactive, watch } from 'vue'
import _ from 'lodash'
// local
import { SuggestI } from '@/interfaces'
import { getAutoComplete } from '@/requests'

const suggest = reactive({
  disabled: false,
  query: '',
  results: [],
  _error: null,
  _loading: false
} as SuggestI)

export const useSuggest = () => {
  const getSuggestResults = _.debounce(async (val: string) => {
    suggest._loading = true
    const response = await getAutoComplete(val)
    if (response) {
      if (response.error) suggest._error = response.error
      // check if results are still relevant before updating list
      if (val === suggest.query) suggest.results = response.results
    } else console.error('Nothing returned from getAutoComplete fn.')
    suggest._loading = false
  }, 200)
  const suggestActive = computed(() => suggest.results.length > 0 && !suggest.disabled)

  watch(() => suggest.query, (val) => {
    if (val?.trim().length > 2 && !suggest.disabled) getSuggestResults(val)
    else suggest.results = []
  })
  return {
    suggest,
    getSuggestResults,
    suggestActive
  }
}